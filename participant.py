import paho.mqtt.client as mqtt
import json
import time
import random
import threading

# =========================
# CONSTANTES MQTT
# =========================
TOPIC_INIT = "ppd/init"
TOPIC_VOTE = "ppd/vote"
TOPIC_LEADER = "ppd/leader"
TOPIC_CHALLENGE = "ppd/challenge"
TOPIC_SOLUTION = "ppd/solution"

STATE_INIT = 0
STATE_ELECTION = 1
STATE_RUNNING = 2


# =========================
# CLASSE PRINCIPAL
# =========================
class Participant:
    def __init__(self, broker_host, broker_port):
        self.broker_host = broker_host
        self.broker_port = broker_port

        # CLIENT ID ÚNICO
        self.client_id = random.randint(1, 65000)

        # Descoberta automática
        self.known_clients = set()
        self.discovery_started_at = None
        self.last_new_client_at = None
        self.DISCOVERY_TIMEOUT = 5.0  # segundos sem novos participantes

        # Eleição
        self.state = STATE_INIT
        self.votes = {}
        self.vote_id = random.randint(1, 99999)
        self.leader = None

        # MQTT
        self.mqtt_client = mqtt.Client(client_id=f"ppd-{self.client_id}")
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    # =========================
    # MQTT CALLBACKS
    # =========================
    def on_connect(self, client, userdata, flags, rc):
        print(f"[{self.client_id}] Conectado ao broker ({rc})")

        client.subscribe(TOPIC_INIT)
        client.subscribe(TOPIC_VOTE)
        client.subscribe(TOPIC_LEADER)
        client.subscribe(TOPIC_CHALLENGE)
        client.subscribe(TOPIC_SOLUTION)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode()
        data = json.loads(payload)

        if msg.topic == TOPIC_INIT and self.state == STATE_INIT:
            sender = data["client_id"]

            if self.discovery_started_at is None:
                self.discovery_started_at = time.time()

            if sender not in self.known_clients:
                self.known_clients.add(sender)
                self.last_new_client_at = time.time()

            print(f"[{self.client_id}] (INIT) Recebi ClientID={sender}. Total={len(self.known_clients)}")

        elif msg.topic == TOPIC_VOTE and self.state == STATE_ELECTION:
            cid = data["client_id"]
            vid = data["vote_id"]
            self.votes[cid] = vid
            print(f"[{self.client_id}] (ELECTION) Recebi voto: {cid} → {vid}")

            if len(self.votes) == len(self.known_clients):
                self.decide_leader()

        elif msg.topic == TOPIC_LEADER and self.state == STATE_RUNNING:
            self.leader = data["leader"]
            print(f"[{self.client_id}] Líder definido: {self.leader}")

        elif msg.topic == TOPIC_CHALLENGE:
            print(f"[{self.client_id}] Desafio recebido: {data}")

        elif msg.topic == TOPIC_SOLUTION:
            print(f"[{self.client_id}] Solução recebida: {data}")

    # =========================
    # FUNÇÕES DA FASE INIT
    # =========================
    def publish_init(self):
        msg = {"client_id": self.client_id}
        self.mqtt_client.publish(TOPIC_INIT, json.dumps(msg))

    def check_discovery_finished(self):
        if self.discovery_started_at is None:
            return False

        agora = time.time()
        base = self.last_new_client_at or self.discovery_started_at

        if agora - base >= self.DISCOVERY_TIMEOUT:
            print(f"\n[{self.client_id}] (INIT) Descoberta encerrada.")
            print(f"[{self.client_id}] Clientes finais: {self.known_clients}\n")
            self.state = STATE_ELECTION
            self.start_election()
            return True

        return False

    # =========================
    # ELEIÇÃO DE LÍDER
    # =========================
    def start_election(self):
        print(f"[{self.client_id}] === FASE ELECTION ===")
        msg = {"client_id": self.client_id, "vote_id": self.vote_id}
        self.votes[self.client_id] = self.vote_id
        self.mqtt_client.publish(TOPIC_VOTE, json.dumps(msg))

    def decide_leader(self):
        winner = max(self.votes.values())
        for cid, vid in self.votes.items():
            if vid == winner:
                self.leader = cid
                break

        print(f"\n[{self.client_id}] Líder eleito: {self.leader}\n")

        msg = {"leader": self.leader}
        self.mqtt_client.publish(TOPIC_LEADER, json.dumps(msg))

        self.state = STATE_RUNNING

        if self.leader == self.client_id:
            self.start_challenge()

    # =========================
    # FASE LÍDER / DESAFIO
    # =========================
    def start_challenge(self):
        print(f"[{self.client_id}] SOU O LÍDER – publicando desafio.")
        msg = {"challenge": "hash_aleatorio", "txid": 1}
        self.mqtt_client.publish(TOPIC_CHALLENGE, json.dumps(msg))

    # =========================
    # LOOP PRINCIPAL
    # =========================
    def run(self):
        self.mqtt_client.connect(self.broker_host, self.broker_port, 60)
        self.mqtt_client.loop_start()

        while True:
            if self.state == STATE_INIT:
                self.publish_init()
                self.check_discovery_finished()

            time.sleep(1)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--broker", type=str, default="broker.emqx.io")
    parser.add_argument("--port", type=int, default=1883)
    args = parser.parse_args()

    p = Participant(broker_host=args.broker, broker_port=args.port)
    p.run()
