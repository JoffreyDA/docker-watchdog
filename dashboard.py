import streamlit as st
import docker

st.set_page_config(page_title="Docker Watchdog", layout="wide")
st.title("📦 Docker Watchdog Dashboard")

client = docker.from_env()
containers = client.containers.list(all=True)

data = []
for c in containers:
    stats = {
        "Nom": c.name,
        "Image": c.image.tags[0] if c.image.tags else "inconnu",
        "Statut": c.status
    }

    if c.status == "running":
        s = c.stats(stream=False)
        mem = s['memory_stats']['usage'] / (1024 ** 2)
        cpu_delta = s['cpu_stats']['cpu_usage']['total_usage'] - s['precpu_stats']['cpu_usage']['total_usage']
        sys_delta = s['cpu_stats']['system_cpu_usage'] - s['precpu_stats']['system_cpu_usage']
        cpu = (cpu_delta / sys_delta) * 100 if sys_delta > 0 else 0
        rx = tx = 0
        for iface in s.get('networks', {}).values():
            rx += iface.get('rx_bytes', 0)
            tx += iface.get('tx_bytes', 0)
        stats.update({
            "CPU (%)": round(cpu, 2),
            "Mémoire (Mo)": round(mem, 2),
            "Rx (Ko)": round(rx / 1024, 2),
            "Tx (Ko)": round(tx / 1024, 2)
        })
    else:
        stats.update({
            "CPU (%)": "-",
            "Mémoire (Mo)": "-",
            "Rx (Ko)": "-",
            "Tx (Ko)": "-"
        })

    data.append(stats)

st.dataframe(data, use_container_width=True)
