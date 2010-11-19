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
	/** Called when the activity is first created. */

	private TextView connectionStatus;
	private PrintWriter hostWriter;
	private EditText hostInput;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		this.connectionStatus = (TextView) this
				.findViewById(R.id.connection_view);
		this.hostInput = (EditText) this.findViewById(R.id.host_address);
	}


	public void next(final View v) {
		sendMsg("next");
	}
	
	public void prev(final View v) {
		sendMsg("prev");
	}
	
	public void playPause(final View v) {
		sendMsg("play_pause");
	}

	public void cycle(final View v) {
		sendMsg("cycle");
	}
	
	public void toggleShuffle(final View v){
		sendMsg("toggle_shuffle");
	}
	
	public void toggleRepeat(final View v){
		sendMsg("toggle_repeat");
	}
	
	public void volUp(final View v){
		sendMsg("louder");
	}
	
	public void volDown(final View v){
		sendMsg("quieter");
	}
	
	public void connect(final View v) {
		try {
			this.hostWriter = connectToHost(this.hostInput
					.getEditableText().toString());
			this.connectionStatus.setText(this
					.getString(R.string.connected)
					+ this.hostInput.getEditableText().toString());
		} catch (UnknownHostException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private void sendMsg(String msg) {
		this.hostWriter.println(msg);
	}

	public PrintWriter connectToHost(String host) throws UnknownHostException,
			IOException {
		Socket s = new Socket(host, 9006);
		return new PrintWriter(s.getOutputStream(), true);
	}

}