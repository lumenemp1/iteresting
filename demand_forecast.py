import pandas as pd
from prophet import Prophet
from datetime import timedelta
import os

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE_MAP = {
    "eon": os.path.join(BASE_DIR, "sorted_file.xlsx"),
    "sdp": os.path.join(BASE_DIR, "sorted_file_sdp.xlsx"),
    "orion": os.path.join(BASE_DIR, "sorted_file_orion.xlsx"),
}

# ---------- LOAD DATA ----------
def load_data(source_system):
    if source_system not in SOURCE_FILE_MAP:
        raise ValueError(f"Unknown source system: {source_system}")
    
    df = pd.read_excel(SOURCE_FILE_MAP[source_system])
    df.rename(columns={"date": "ds", "total_orders": "y", "product": "product_name"}, inplace=True)
    df["ds"] = pd.to_datetime(df["ds"])
    return df

def get_all_products_eon():
    df = load_data("eon")
    return sorted(df['product_name'].unique().tolist())

# ---------- HELPER FUNCTION TO CHECK DATA SUFFICIENCY ----------
def has_sufficient_data(df_prod):
    """Check if product has sufficient data for Prophet forecasting"""
    return df_prod.shape[0] >= 60 and df_prod["y"].sum() >= 10

# ---------- SUMMARY (FILTERED PRODUCT LIST) ----------
def get_forecast_summary(source_system):
    """Return only products that have sufficient data for forecasting"""
    df = load_data(source_system)
    all_products = df['product_name'].unique()
    
    # Filter products that have sufficient data
    valid_products = []
    for product in all_products:
        df_prod = df[df["product_name"] == product][["ds", "y"]].copy()
        if has_sufficient_data(df_prod):
            valid_products.append(product)
    
    return sorted(valid_products)

# ---------- DETAILED FORECAST (PER PRODUCT) ----------
def get_forecast_detail(source_system, product):
    df = load_data(source_system)
    df_prod = df[df["product_name"] == product][["ds", "y"]].copy()

    # Only forecast if there's sufficient data
    if has_sufficient_data(df_prod):
        model = Prophet(daily_seasonality=True, yearly_seasonality=True)
        model.fit(df_prod)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        forecast["yhat"] = forecast["yhat"].clip(lower=0)
        forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
        forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

        forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()

        # Filter to only return next 30 days
        latest_cutoff = forecast["ds"].max() - timedelta(days=29)
        df_selected = forecast[forecast["ds"] >= latest_cutoff]

        return {
            "product": product,
            "total_forecast": round(df_selected["yhat"].sum(), 2),
            "forecast_data": df_selected.to_dict(orient="records")
        }
    
    # Return None or empty result if insufficient data
    return None

# ---------- OPTIONAL: GET DATA STATISTICS ----------
def get_data_statistics(source_system):
    """Get statistics about data availability for debugging"""
    df = load_data(source_system)
    all_products = df['product_name'].unique()
    
    stats = {
        "total_products": len(all_products),
        "products_with_sufficient_data": 0,
        "products_with_insufficient_data": 0,
        "details": []
    }
    
    for product in all_products:
        df_prod = df[df["product_name"] == product][["ds", "y"]].copy()
        row_count = df_prod.shape[0]
        total_orders = df_prod["y"].sum()
        sufficient = has_sufficient_data(df_prod)
        
        if sufficient:
            stats["products_with_sufficient_data"] += 1
        else:
            stats["products_with_insufficient_data"] += 1
            
        stats["details"].append({
            "product": product,
            "row_count": row_count,
            "total_orders": total_orders,
            "sufficient_data": sufficient
        })
    
    return stats



app.py

### ----- DEMAND FORECASTING ROUTES ----- ###
@app.route("/forecast/summary", methods=["POST"])
def forecast_summary():
    data = request.get_json()
    source = data.get("source_system")

    if not source:
        return jsonify({"error": "Missing source_system"}), 400

    try:
        product_list = get_forecast_summary(source)
        return jsonify({"products": product_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/forecast/detail", methods=["POST"])
def forecast_detail():
    data = request.get_json()
    source = data.get("source_system")
    product = data.get("product")

    if not source or not product:
        return jsonify({"error": "Missing source_system or product"}), 400

    try:
        forecast = get_forecast_detail(source, product)
        return jsonify(forecast)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
