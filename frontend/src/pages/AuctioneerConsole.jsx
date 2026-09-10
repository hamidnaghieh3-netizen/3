import { useEffect, useState } from "react";

export default function AuctioneerConsole({ auctionId }) {
  const [ws, setWs] = useState(null);
  const [log, setLog] = useState([]);

  useEffect(() => {
    const socket = new WebSocket(
      `ws://localhost:8000/ws/auctions/1`
    );

    socket.onopen = () => {
      setLog((prev) => [...prev, "Connected to auction channel"]);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLog((prev) => [...prev, JSON.stringify(data)]);
    };

    socket.onclose = () => {
      setLog((prev) => [...prev, "Disconnected"]);
    };

    setWs(socket);

    return () => socket.close();
  }, [auctionId]);

  const sendControl = (type) => {
    if (!ws) return;
    ws.send(JSON.stringify({ type }));
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Auctioneer Console — Auction #{auctionId}</h1>

      <div style={{ marginBottom: "20px" }}>
        <button onClick={() => sendControl("start")}>Start Auction</button>
        <button onClick={() => sendControl("pause")}>Pause</button>
        <button onClick={() => sendControl("resume")}>Resume</button>
        <button onClick={() => sendControl("end")}>End Auction</button>
      </div>

      <h2>Live Event Log</h2>
      <div
        style={{
          background: "#f0f0f0",
          padding: "10px",
          height: "300px",
          overflowY: "scroll",
          border: "1px solid #ccc",
        }}
      >
        {log.map((entry, index) => (
          <div key={index}>{entry}</div>
        ))}
      </div>
    </div>
  );
}
