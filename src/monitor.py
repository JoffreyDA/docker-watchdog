import docker
from tabulate import tabulate

# Seuils d'alerte
CPU_SEUIL = 50       # en %
MEM_SEUIL = 200      # en Mo
RX_SEUIL = 10000     # en Ko
TX_SEUIL = 10000     # en Ko

def get_container_stats(container):
    try:
        stats = container.stats(stream=False)
        mem = stats['memory_stats']['usage'] / (1024 ** 2)  # en Mo

        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                    stats['precpu_stats']['cpu_usage']['total_usage']
        sys_delta = stats['cpu_stats']['system_cpu_usage'] - \
                    stats['precpu_stats']['system_cpu_usage']

        cpu = (cpu_delta / sys_delta) * 100 if sys_delta > 0 else 0

        rx = tx = 0
        for net in stats.get("networks", {}).values():
            rx += net.get("rx_bytes", 0)
            tx += net.get("tx_bytes", 0)

        return {
            "CPU (%)": round(cpu, 2),
            "Mémoire (Mo)": round(mem, 2),
            "Rx (Ko)": round(rx / 1024, 2),
            "Tx (Ko)": round(tx / 1024, 2)
        }

    except Exception as e:
        return {
            "CPU (%)": "-",
            "Mémoire (Mo)": "-",
            "Rx (Ko)": "-",
            "Tx (Ko)": "-"
        }

def check_alerts(stats):
    alerts = []
    try:
        if stats.get("CPU (%)") != "-" and float(stats["CPU (%)"]) > CPU_SEUIL:
            alerts.append("⚠️ CPU élevé")
        if stats.get("Mémoire (Mo)") != "-" and float(stats["Mémoire (Mo)"]) > MEM_SEUIL:
            alerts.append("⚠️ Mémoire élevée")
        if stats.get("Rx (Ko)") != "-" and float(stats["Rx (Ko)"]) > RX_SEUIL:
            alerts.append("⚠️ Rx élevé")
        if stats.get("Tx (Ko)") != "-" and float(stats["Tx (Ko)"]) > TX_SEUIL:
            alerts.append("⚠️ Tx élevé")
    except:
        pass
    return alerts

def list_containers():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    data = []

    for container in containers:
        infos = {
            "Nom": container.name,
            "Image": container.image.tags[0] if container.image.tags else "inconnu",
            "Statut": container.status
        }

        if container.status == "running":
            stats = get_container_stats(container)
            infos.update(stats)
            infos["Alertes"] = ", ".join(check_alerts(stats))
        else:
            infos.update({
                "CPU (%)": "-",
                "Mémoire (Mo)": "-",
                "Rx (Ko)": "-",
                "Tx (Ko)": "-",
                "Alertes": "-"
            })

        data.append(infos)

    print(tabulate(data, headers="keys", tablefmt="fancy_grid"))

if __name__ == "__main__":
    list_containers()
