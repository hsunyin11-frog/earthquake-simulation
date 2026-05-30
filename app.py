import streamlit as st
import pandas as pd
import geopandas as gpd
import numpy as np
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
import math
from dataclasses import dataclass, field
from typing import List

# --- 1. 定義資料結構 ---
@dataclass
class Shelter:
    id: str
    name: str
    lat: float
    lon: float
    capacity: int
    city: str = ""
    district: str = ""
    village: str = ""
    address: str = ""
    allocated: int = field(default=0, repr=False)

    @property
    def remaining(self) -> int:
        return self.capacity - self.allocated

    @property
    def utilisation(self) -> float:
        if self.capacity == 0:
            return float("inf")
        return self.allocated / self.capacity

@dataclass
class Flow:
    from_zone: str
    to_shelter: str
    to_shelter_id: str
    people: int
    overflow: bool = False

    def to_dict(self) -> dict:
        return {
            "from_zone": self.from_zone,
            "to_shelter": self.to_shelter,
            "to_shelter_id": self.to_shelter_id,
            "people": self.people,
            "overflow": self.overflow,
        }

# --- 2. 數學與地震模擬公式 ---
def haversine_distance(lat1, lon1, lat2, lon2):
    earth_radius = 6371.0
    rad_lat1, rad_lon1 = np.radians(lat1), np.radians(lon1)
    rad_lat2, rad_lon2 = np.radians(lat2), np.radians(lon2)
    dlat = rad_lat2 - rad_lat1
    dlon = rad_lon2 - rad_lon1
    a = np.sin(dlat / 2)**2 + np.cos(rad_lat1) * np.cos(rad_lat2) * np.sin(dlon / 2)**2
    return earth_radius * (2 * np.arcsin(np.sqrt(a)))

def calculate_pga(magnitude, distance):
    A, B, C, D = 0.026, 1.28, 10.0, 1.5
    base_pga = (A * np.exp(B * magnitude)) / ((distance + C) ** D)
    return base_pga * 980

def get_intensity_level(pga):
    if pga < 0.8: return "0級"
    elif pga < 2.5: return "1級"
    elif pga < 8.0: return "2級"
    elif pga < 25.0: return "3級"
    elif pga < 80.0: return "4級"
    elif pga < 140.0: return "5弱"
    elif pga < 250.0: return "5強"
    elif pga < 440.0: return "6弱"
    elif pga < 800.0: return "6強"
    else: return "7級"

def get_damage_rate(intensity):
    damage_table = {"4級": 0.01, "5弱": 0.05, "5強": 0.15, "6弱": 0.35, "6強": 0.60, "7級": 0.85}
    return damage_table.get(intensity, 0.00)

def normalize_name(text):
    return str(text).replace("/", "").replace(" ", "").replace("_", "").replace("-", "").replace("臺", "台").replace("蔀", "廍").strip()

def fix_mojibake(text):
    try: return str(text).encode("latin1").decode("utf-8")
    except: return str(text)

def risk_color(risk):
    if risk >= 0.8: return "#ff0000"
    elif risk >= 0.5: return "#ff8800"
    elif risk > 0: return "#ffff00"
    else: return "#cccccc"

# --- 3. 核心模擬器 ---
def run_simulation(epicenter_lat, epicenter_lon, magnitude, area_df):
    results = []
    for idx, row in area_df.iterrows():
        dist = haversine_distance(epicenter_lat, epicenter_lon, row['lat'], row['lon'])
        pga = calculate_pga(magnitude, dist)
        intensity = get_intensity_level(pga)
        damage_rate = get_damage_rate(intensity)
        predicted_refugees = int(row['population'] * row['old house ratio'] * damage_rate * 0.8)

        results.append({
            '行政區': row['name1'],
            '里名': row['name2'],
            'lat': row['lat'],
            'lon': row['lon'],
            '震央距離_km': round(dist, 2),
            '預估PGA': round(pga, 2),
            '預估震度': intensity,
            '預估避難人數': predicted_refugees
        })
    return pd.DataFrame(results)

def greedy_allocate(impact_data, shelters):
    flows = []
    sorted_zones = sorted(impact_data, key=lambda z: int(z["預估避難人數"]), reverse=True)
    
    for zone in sorted_zones:
        remaining = int(zone["預估避難人數"])
        if remaining <= 0: continue
        label = f"{zone['行政區']}-{zone['里名']}"
        
        by_dist = sorted(shelters, key=lambda s: haversine_distance(float(zone["lat"]), float(zone["lon"]), s.lat, s.lon))
        
        for shelter in by_dist:
            if remaining <= 0: break
            avail = shelter.remaining
            if avail <= 0: continue
            
            send = min(remaining, avail)
            shelter.allocated += send
            remaining -= send
            flows.append(Flow(from_zone=label, to_shelter=shelter.name, to_shelter_id=shelter.id, people=send, overflow=False))
            
        if remaining > 0:
            fallback = min(by_dist, key=lambda s: s.utilisation)
            fallback.allocated += remaining
            flows.append(Flow(from_zone=label, to_shelter=fallback.name, to_shelter_id=fallback.id, people=remaining, overflow=True))
    return flows

# --- 4. 網頁介面與狀態記憶 (Streamlit) ---
st.set_page_config(page_title="地震避難模擬", layout="wide")
st.title("🌍 地震避難人數與收容所分配模擬系統")

# 給系統一個記憶體，避免按鈕點擊後地圖閃退
if "simulated" not in st.session_state:
    st.session_state.simulated = False

# 左側設定欄
st.sidebar.header("⚙️ 設定地震參數")
epi_lat = st.sidebar.number_input("震央緯度", value=24.15, step=0.01)
epi_lon = st.sidebar.number_input("震央經度", value=121.62, step=0.01)
mag = st.sidebar.number_input("地震規模", value=6.0, step=0.1)

# 當使用者按下按鈕時，更新系統記憶
if st.sidebar.button("🚀 執行模擬"):
    st.session_state.simulated = True

# 快取資料讀取 (避免每次點擊都重新讀取 Shapefile)
@st.cache_data
def load_data():
    shelter_df = pd.read_csv("shelter.csv", encoding="utf-8-sig", dtype=str)
    village_df = pd.read_csv("village.csv", encoding="utf-8-sig", dtype=str)
    gdf = gpd.read_file("village_boundary.shp")
    
    # 基本清理
    shelter_df.columns = [c.strip() for c in shelter_df.columns]
    village_df.columns = [c.strip() for c in village_df.columns]
    gdf.columns = [c.strip() for c in gdf.columns]
    
    shelter_df["lat"] = shelter_df["lat"].astype(float)
    shelter_df["lon"] = shelter_df["lon"].astype(float)
    shelter_df["capacity"] = pd.to_numeric(shelter_df["capacity"], errors="coerce")
    shelter_df = shelter_df.dropna(subset=["capacity", "lat", "lon"]).copy()
    shelter_df["capacity"] = shelter_df["capacity"].astype(int)
    
    village_df["lat"] = village_df["lat"].astype(float)
    village_df["lon"] = village_df["lon"].astype(float)
    village_df["population"] = pd.to_numeric(village_df["population"], errors="coerce").fillna(0).astype(int)
    village_df["old house ratio"] = pd.to_numeric(village_df["old house ratio"], errors="coerce").fillna(0)
    
    return shelter_df, village_df, gdf

# 如果系統記憶體顯示已執行模擬，就開始畫圖表
if st.session_state.simulated:
    with st.spinner("正在計算受災程度與分配避難所..."):
        shelter_df, village_df, gdf = load_data()
        
        # 1. 執行模擬
        df_output = run_simulation(epi_lat, epi_lon, mag, village_df)
        
        # 2. 建立避難所物件
        shelters = []
        for _, row in shelter_df.iterrows():
            shelters.append(Shelter(id=str(row["id"]), name=str(row["name"]), lat=row["lat"], lon=row["lon"], capacity=row["capacity"], city=row.get("city", ""), district=row.get("district", ""), village=row.get("village", ""), address=row.get("address", "")))
            
        # 3. 執行分配
        impact_data = df_output.to_dict(orient="records")
        flows = greedy_allocate(impact_data, shelters)
        flows_df = pd.DataFrame([f.to_dict() for f in flows])
        
        if not flows_df.empty:
            flows_df[["行政區", "里名"]] = flows_df["from_zone"].str.split("-", n=1, expand=True)
            assigned_shelter_df = flows_df.merge(shelter_df, left_on="to_shelter_id", right_on="id", how="left")
            assigned_shelter_df = assigned_shelter_df.dropna(subset=["lat", "lon"]).copy()
        
        # 4. 準備地圖資料
        max_pga = df_output["預估PGA"].max()
        df_output["risk_score"] = df_output["預估PGA"] / max_pga if max_pga > 0 else 0
        df_output["merge_name"] = (df_output["行政區"].astype(str) + df_output["里名"].astype(str)).apply(normalize_name)
        
        # 尋找 Shapefile 欄位
        v_col_candidates = [c for c in gdf.columns if c in ["VILLNAME", "TVNAME", "村里名", "里名", "name2", "village"]]
        v_col = v_col_candidates[0] if v_col_candidates else gdf.columns[0]
        
        d_col_candidates = [c for c in gdf.columns if c in ["TOWNNAME", "TOWN", "行政區", "name1", "district"]]
        d_col = d_col_candidates[0] if d_col_candidates else None
        
        gdf["shp_village_fix"] = gdf[v_col].apply(fix_mojibake)
        if d_col:
            gdf["shp_district_fix"] = gdf[d_col].apply(fix_mojibake)
            gdf["merge_name"] = (gdf["shp_district_fix"] + gdf["shp_village_fix"]).apply(normalize_name)
        else:
            gdf["merge_name"] = gdf["shp_village_fix"].apply(normalize_name)
            
        map_df = gdf.merge(df_output[["merge_name", "risk_score", "預估避難人數", "行政區", "里名"]], on="merge_name", how="left")
        map_df["risk_score"] = map_df["risk_score"].fillna(0)
        
        # 5. 繪製地圖
        st.subheader("🗺️ 災情與避難所分配地圖")
        m = folium.Map(location=[epi_lat, epi_lon], zoom_start=11)
        
        folium.GeoJson(
            map_df,
            style_function=lambda feature: {
                "fillColor": risk_color(feature["properties"].get("risk_score", 0)),
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.7 if feature["properties"].get("risk_score", 0) > 0 else 0.1,
            },
            tooltip=folium.GeoJsonTooltip(fields=["行政區", "里名", "預估避難人數"], aliases=["行政區", "里名", "預估避難人數"])
        ).add_to(m)
        
        if not flows_df.empty:
            marker_cluster = MarkerCluster(name="已分配避難所").add_to(m)
            for _, row in assigned_shelter_df.iterrows():
                folium.Marker(
                    location=[float(row["lat"]), float(row["lon"])],
                    tooltip=f"{row['to_shelter']}｜分配 {row['people']} 人",
                    icon=folium.Icon(color="red" if bool(row["overflow"]) else "blue", icon="home")
                ).add_to(marker_cluster)
                
        # 使用 Streamlit 原生 HTML 渲染地圖，穩定不閃退
        components.html(m._repr_html_(), height=600)
        
        # 顯示表格
        st.subheader("📊 受災與分配明細")
        col1, col2 = st.columns(2)
        with col1:
            st.write("各里預估避難人數")
            st.dataframe(df_output[["行政區", "里名", "預估震度", "預估避難人數"]].sort_values("預估避難人數", ascending=False))
        with col2:
            st.write("避難所分配結果")
            if not flows_df.empty:
                # Format overflow column with emoji for clarity
                display_flows = flows_df.copy()
                display_flows["overflow"] = display_flows["overflow"].map(lambda x: "⚠️ 超額" if x else "✓ 正常")
                display_flows = display_flows.rename(columns={
                    "from_zone": "來源里別",
                    "to_shelter": "避難所",
                    "people": "分配人數",
                    "overflow": "分配狀態"
                })
                st.dataframe(display_flows[["來源里別", "避難所", "分配人數", "分配狀態"]], use_container_width=True)
        
        # STATISTICS DASHBOARD
        st.subheader("📈 避難所容量統計")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        total_refugees = df_output["預估避難人數"].sum()
        total_capacity = shelter_df["capacity"].sum()
        total_allocated = sum(s.allocated for s in shelters)
        utilization_rate = (total_allocated / total_capacity * 100) if total_capacity > 0 else 0
        
        with stats_col1:
            st.metric("預估難民總數", f"{total_refugees:,} 人")
        with stats_col2:
            st.metric("收容所總容量", f"{total_capacity:,} 人")
        with stats_col3:
            st.metric("已分配人數", f"{total_allocated:,} 人")
        with stats_col4:
            st.metric("容量使用率", f"{utilization_rate:.1f}%", delta="超容" if total_allocated > total_capacity else "正常")
        
        # SHELTER STATUS TABLE
        st.subheader("🏢 各收容所詳細狀態")
        shelter_status = pd.DataFrame([
            {
                "避難所": s.name,
                "容量": s.capacity,
                "已分配": s.allocated,
                "剩餘": s.remaining,
                "使用率": f"{min(s.utilisation * 100, 999):.1f}%",
                "狀態": "⚠️ 超額" if s.remaining < 0 else "✓ 正常" if s.remaining > s.capacity * 0.2 else "⚡ 即將滿載"
            }
            for s in shelters
        ]).sort_values("使用率", ascending=False)
        st.dataframe(shelter_status, use_container_width=True)
        
        # DISTANCE DISTRIBUTION CHART
        st.subheader("📊 避難距離分佈")
        if not flows_df.empty:
            # Calculate distances for each flow
            flows_df_with_dist = flows_df.copy()
            for idx, row in flows_df_with_dist.iterrows():
                zone_data = df_output[df_output["里名"] == row["from_zone"].split("-")[1]]
                if not zone_data.empty:
                    zone_lat, zone_lon = zone_data.iloc[0][["lat", "lon"]]
                    shelter_row = assigned_shelter_df[assigned_shelter_df["to_shelter_id"] == row["to_shelter_id"]]
                    if not shelter_row.empty:
                        shelter_lat, shelter_lon = shelter_row.iloc[0][["lat", "lon"]]
                        dist = haversine_distance(zone_lat, zone_lon, shelter_lat, shelter_lon)
                        flows_df_with_dist.at[idx, "距離_km"] = round(dist, 2)
            
            st.bar_chart(flows_df_with_dist.groupby("距離_km")["people"].sum())
        
        # SCENARIO COMPARISON (Optional)
        st.subheader("🔄 快速場景比較")
        if st.checkbox("顯示多震度對比"):
            comp_mags = st.multiselect("選擇要比較的地震規模", [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5], default=[mag])
            for comp_mag in comp_mags:
                comp_df = run_simulation(epi_lat, epi_lon, comp_mag, village_df)
                refugees_count = comp_df["預估避難人數"].sum()
                st.write(f"規模 {comp_mag}: {refugees_count:,} 人")
