package pl.rzubr;

import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import android.R.bool;
import android.app.Activity;
import android.opengl.Visibility;
import android.os.Bundle;
import android.os.Handler;
import android.view.KeyEvent;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.AdapterView.OnItemSelectedListener;

public class Dromote extends Activity {

	private static final String TAG = "Dromote";
	private final Handler mHandler = new Handler();

	private MPRISSocket player = new MPRISSocket(9006);
	private volatile Thread checker;
	private TextView status;
	private String nowPlaying = "";
	private String[] playerList = new String[0];

	private final Runnable mUpdateNowPlaying = new Runnable() {
		public void run() {
			status.setText(nowPlaying);
		}
	};

	private final Runnable mBye = new Runnable() {
		public void run() {
			;
			player.disconnect();
			updateConnInfo(player.isConnected(), "");
			nowPlaying = "";
			status.setText(nowPlaying);
		}
	};

	private final Runnable mUpdatePlayerList = new Runnable() {
		public void run() {
			ArrayAdapter<CharSequence> adapter = new ArrayAdapter<CharSequence>(
					Dromote.this, android.R.layout.simple_spinner_item,
					playerList);
			adapter
					.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
			Spinner spinner = (Spinner) findViewById(R.id.spinner);
			spinner.setAdapter(adapter);
			spinner.setOnItemSelectedListener(new MyOnItemSelectedListener());
			spinner.setVisibility(1);

		}
	};

	private Runnable socketChecker = new Runnable() {

		private boolean players = false;

		public void run() {
			while (true) {
				while (player.isConnected() && !player.bye) {
					String data = player.getData();
					if (players) {
						players = false;
						playerList = data.split(" ");
						mHandler.post(mUpdatePlayerList);
					} else {
						if (data.equals("bye")) {
							player.bye = true;
							mHandler.post(mBye);
						} else if (data.equals("PLAYERS")) {
							players = true;
						} else {
							nowPlaying = data;
							mHandler.post(mUpdateNowPlaying);
						}
					}
				}
			}
		}
	};

	private void update_now_playing(String title) {
		status.setText(title);
	}

	public class MyOnItemSelectedListener implements OnItemSelectedListener {

		public void onItemSelected(AdapterView<?> parent, View view, int pos,
				long id) {
			player.sendCommand("cycle " + pos);
		}

		public void onNothingSelected(AdapterView parent) {
			// Do nothing.
		}
	}

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		EditText hostInput = (EditText) this.findViewById(R.id.host_address);

		hostInput
				.setOnEditorActionListener(new TextView.OnEditorActionListener() {
					@Override
					public boolean onEditorAction(TextView v, int actionId,
							KeyEvent event) {
						Dromote.this.connect(null);
						return false;
					}
				});
		status = (TextView) this.findViewById(R.id.now_playing);
		checker = new Thread(socketChecker);
		checker.start();

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

	public void disconnect(final View v) {
		this.player.sendCommand("bye");

	}

	private void updateConnInfo(boolean connected, String hostAddress) {
		Button connect = (Button) this.findViewById(R.id.connect_button);
		Button disconnect = (Button) this.findViewById(R.id.disconnect_button);
		if (connected) {
			disconnect.setText("Disconnect " + hostAddress);
			disconnect.setEnabled(true);
		} else {
			disconnect.setText("Disconnect");
			disconnect.setEnabled(false);
		}
	}

}