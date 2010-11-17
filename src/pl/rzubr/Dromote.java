package pl.rzubr;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;

import android.app.Activity;
import android.os.Bundle;
import android.text.Editable;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;

public class Dromote extends Activity implements OnClickListener {
	/** Called when the activity is first created. */

	private Button playPauseButton;
	private Button connectButton;
	private Button nextButton;
	private Button prevButton;
	private Button cycle;
	private TextView connectionStatus;
	private PrintWriter hostWriter;
	private EditText hostInput;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		this.playPauseButton = (Button) this.findViewById(R.id.action_button);
		this.connectionStatus = (TextView) this
				.findViewById(R.id.connection_view);
		this.connectButton = (Button) this.findViewById(R.id.connect_button);
		this.hostInput = (EditText) this.findViewById(R.id.host_address);
		this.nextButton = (Button) this.findViewById(R.id.next_button);
		this.prevButton = (Button) this.findViewById(R.id.prev_button);
		this.cycle = (Button) this.findViewById(R.id.cycle_button);

		this.playPauseButton.setOnClickListener(this);
		this.connectButton.setOnClickListener(this);
		this.nextButton.setOnClickListener(this);
		this.prevButton.setOnClickListener(this);
		this.cycle.setOnClickListener(this);

	}

	@Override
	public void onClick(View src) {
		switch (src.getId()) {
		case R.id.connect_button:
			try {
				this.hostWriter = connectToHost(this.hostInput.getEditableText().toString());
				this.connectionStatus.setText(this.getString(R.string.connected) + this.hostInput.getEditableText().toString());
			} catch (UnknownHostException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
			break;
		case R.id.action_button:
			this.hostWriter.println("play_pause");
			break;
		case R.id.next_button:
			this.hostWriter.println("next");
			break;
		case R.id.prev_button:
			this.hostWriter.println("prev");
			break;	
		case R.id.cycle_button:
			this.hostWriter.println("cycle");
			break;	
		}

	}

	public PrintWriter connectToHost(String host) throws UnknownHostException,
			IOException {
		Socket s = new Socket(host, 9006);
		return new PrintWriter(s.getOutputStream(), true);

	}

}