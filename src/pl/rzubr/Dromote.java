package pl.rzubr;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

import org.apache.http.impl.conn.tsccm.WaitingThread;

import android.app.Activity;
import android.os.Bundle;
import android.text.Editable;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class Dromote extends Activity {

	private MPRISSocket player = new MPRISSocket();

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
	}
	
	public void onDestroy() {
		player.disconnect();
	}

	public void next(final View v) {
		this.player.sendCommand("next");
	}

	public void prev(final View v) {
		this.player.sendCommand("prev");
	}

	public void playPause(final View v) {
		this.player.sendCommand("play_pause");
	}

	public void cycle(final View v) {
		this.player.sendCommand("cycle");
	}

	public void toggleShuffle(final View v) {
		this.player.sendCommand("toggle_shuffle");
	}

	public void toggleRepeat(final View v) {
		this.player.sendCommand("toggle_repeat");
	}

	public void volUp(final View v) {
		this.player.sendCommand("louder");
	}

	public void volDown(final View v) {
		this.player.sendCommand("quieter");
	}

	public void connect(final View v) {
		EditText hostInput = (EditText) this.findViewById(R.id.host_address);
		String hostAddress = hostInput.getEditableText().toString();
		player.connect(hostAddress);
		updateConnInfo(player.isConnected(), hostAddress);
	}

	private void updateConnInfo(boolean connected, String hostAddress) {
		TextView connectionStatus = (TextView) this
		.findViewById(R.id.connection_view);
		if (connected) {
			connectionStatus.setText(this.getString(R.string.connected)
					+ hostAddress);
		} else {
			connectionStatus.setText(this.getString(R.string.conn_error)
					+ hostAddress);
		}
	}

	private class MPRISSocket {
		private Socket serverConnection;
		private PrintWriter cmdWriter;
		private boolean connected = false;

		public boolean connect(String host) {
			if (isConnected())
				disconnect();
			try {
				serverConnection = new Socket(host, 9006);
				cmdWriter = new PrintWriter(
						this.serverConnection.getOutputStream(), true);
				connected = true;
			} catch (UnknownHostException e) {
				return false;
			} catch (IOException e) {
				return false;
			}
			return true;
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

		public void sendCommand(String cmd) {
			if (connected) {
				cmdWriter.println(cmd);
			}
		}
	}

}