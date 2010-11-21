package pl.rzubr;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

public class MPRISSocket {
	private Socket serverConnection;
	private PrintWriter cmdWriter;
	private boolean connected = false;
	private String hostname;
	private int port;
	
	public MPRISSocket(int port){
		this.port = port;
	}

	public void connect(String host) {
		if (isConnected())
			disconnect();
		try {
			serverConnection = new Socket(host, port);
			cmdWriter = new PrintWriter(
					this.serverConnection.getOutputStream(), true);
			connected = true;
			hostname = host;
		} catch (UnknownHostException e) {
			connected = false;
			hostname = null;
		} catch (IOException e) {
			connected = false;
			hostname = null;
		}
	}

	public void disconnect() {
		try {
			sendCommand("bye");
			serverConnection.close();
		} catch (IOException e) {
			e.printStackTrace();
		} finally {
			connected = false;
		}
	}

	public boolean isConnected() {
		return connected;
	}
	
	public void reconnect() {
		if(isConnected()) {
			disconnect();
		}
		connect(hostname);
	}

	public void sendCommand(String cmd) {
		if (connected) {
			cmdWriter.println(cmd);
		}
	}

}