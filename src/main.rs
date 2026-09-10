use constituent_connect::{classify, json_response};
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn write_response(mut stream: TcpStream, status: &str, content_type: &str, body: &str) {
    let headers = format!("HTTP/1.1 {status}\r\nContent-Type: {content_type}\r\nContent-Length: {}\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n", body.len());
    let _ = stream.write_all(format!("{headers}{body}").as_bytes());
}

fn handle(mut stream: TcpStream) {
    let mut buffer = [0_u8; 65536];
    let size = stream.read(&mut buffer).unwrap_or(0);
    let request = String::from_utf8_lossy(&buffer[..size]);
    let first = request.lines().next().unwrap_or("");
    if first.starts_with("GET /health") {
        write_response(stream, "200 OK", "application/json", "{\"status\":\"healthy\",\"mode\":\"local-synthetic\",\"implementation\":\"rust\"}");
    } else if first.starts_with("POST /api/respond") {
        let body = request.split("\r\n\r\n").nth(1).unwrap_or("{}");
        let message = body.split("\"message\":\"").nth(1).and_then(|v| v.split('"').next()).unwrap_or("");
        write_response(stream, "200 OK", "application/json", &json_response(&classify(message)));
    } else {
        let html = "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><title>Maryland Constituent Connect Rust</title></head><body><h1>Maryland Constituent Connect</h1><p>Rust deterministic local-synthetic contact center.</p><p>AI-assisted drafts require human approval. Emergency signals receive 911 guidance; this system cannot dispatch emergency services.</p></body></html>";
        write_response(stream, "200 OK", "text/html; charset=utf-8", html);
    }
}

fn main() {
    let listener = TcpListener::bind("127.0.0.1:8091").expect("bind local Rust server");
    println!("Constituent Connect Rust running at http://127.0.0.1:8091");
    for stream in listener.incoming().flatten() {
        handle(stream);
    }
}
