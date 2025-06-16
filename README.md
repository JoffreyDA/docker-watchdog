# docker-watchdog

Un outil Python pour surveiller les conteneurs Docker.

## Objectif

Lister tous les conteneurs Docker avec leurs noms, images et statuts. Pour les conteneurs actifs, afficher CPU, RAM et trafic réseau.

## Exécution

```bash
python src/monitor.py


---

### ✅ `src/monitor.py`

Voici le **script de base** :

```python
import docker

def list_containers():
    client = docker.from_env()
    containers = client.containers.list(all=True)
    return [
        (
            c.name,
            c.image.tags[0] if c.image.tags else "inconnu",
            c.status
        )
        for c in containers
    ]

if __name__ == "__main__":
    for name, image, status in list_containers():
        print(f"{name:20} | {image:30} | {status}")
