package pl.rzubr;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;

public class Dromote extends Activity {
	
	private static final String TAG = "Dromote";

	private MPRISSocket player = new MPRISSocket(9006);

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
	}
	
	@Override
	public void onStop() {
		super.onStop();
		player.disconnect();
	}
	
	@Override
	public void onStart() {
		super.onStart();
		player.reconnect();
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

}