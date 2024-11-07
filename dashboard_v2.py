from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

app = Flask(__name__)

def load_data(switch_ip):
    csv_file = f"switch_statistics_{switch_ip}.csv"
    return pd.read_csv(csv_file)

@app.route("/")
def dashboard():
    switch_ip = request.args.get("switch_ip", "10.37.0.254")
    data = load_data(switch_ip)
    
    peak_utilization = data["Total Capacity Utilization (%)"].max()
    avg_utilization = data["Total Capacity Utilization (%)"].mean()
    
    fig = px.line(data, x="Timestamp", y="Total Capacity Utilization (%)",
                  title="Total Switch Capacity Utilization Over Time")
    fig.update_layout(xaxis_title="Time", yaxis_title="Utilization (%)")
    graph = fig.to_html(full_html=False)
    
    return render_template("dashboard.html", 
                           peak=peak_utilization, avg=avg_utilization, graph=graph)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)