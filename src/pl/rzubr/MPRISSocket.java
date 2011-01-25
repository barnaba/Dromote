package pl.rzubr;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.Buffer;

import android.R.bool;

public class MPRISSocket {
	private Socket serverConnection;
	private PrintWriter cmdWriter;
	private BufferedReader input;
	private boolean connected = false;
	private String hostname;
	private int port;
	public volatile boolean bye = false;

	public MPRISSocket(int port) {
		this.port = port;
	}

	public void connect(String host) {
		if (isConnected())
			disconnect();
		try {
			serverConnection = new Socket(host, port);
			cmdWriter = new PrintWriter(
					this.serverConnection.getOutputStream(), true);
			input = new BufferedReader(new InputStreamReader(serverConnection
					.getInputStream()));
			connected = true;
			hostname = host;
			bye = false;
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
			serverConnection.shutdownInput();
			serverConnection.shutdownOutput();
			serverConnection.close();
			cmdWriter = null;
			input = null;
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
		if (isConnected()) {
			disconnect();
		}
		connect(hostname);
	}

	public void sendCommand(String cmd) {
		if (connected) {
			cmdWriter.println(cmd);
		}
	}

	public String getData() {
		if (isConnected()) {
			try {
				return input.readLine();
			} catch (IOException e) {
				// nothing
			}
		}
		return "";

	}
}