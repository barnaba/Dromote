package pl.rzubr;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.TextView;

public class Dromote extends Activity {
	/** Called when the activity is first created. */

	private Button playPauseButton;
	private TextView playPauseView;

	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.main);
		this.playPauseButton = (Button) this.findViewById(R.id.button);
		this.playPauseView = (TextView) this.findViewById(R.id.playPauseView);

		this.playPauseButton.setOnClickListener(new OnClickListener() {
			private boolean state = false;

			@Override
			public void onClick(View v) {
				this.state = !this.state;
				if (this.state) {
					Dromote.this.playPauseView.setText(getString(R.string.play));
				} else {
					Dromote.this.playPauseView.setText(getString(R.string.pause));
				}
			}
		});

	}

}