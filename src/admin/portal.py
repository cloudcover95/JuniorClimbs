# path: src/admin/portal.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from typing import Dict

app = FastAPI(title="JuniorClimbs Admin Portal")

# In real deployment this would be protected + use JuniorMemSys

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head><title>JuniorClimbs Admin</title></head>
    <body>
        <h1>JuniorClimbs Admin Dashboard</h1>
        <p>Real-time member status, renewals, balances, and marketing tools.</p>
        <ul>
            <li><a href="/members">Member Directory & Balance</a></li>
            <li><a href="/renewals">Renewal Alerts</a></li>
            <li><a href="/marketing">Campaign Deployment</a></li>
            <li><a href="/waivers">Pending Waivers</a></li>
        </ul>
    </body>
    </html>
    """

@app.get("/members")
def member_directory():
    # Would query data store
    return {"members": "[Live data from JuniorMemSys]"}

# Add more endpoints for balance adjustment, renewal processing, etc.
