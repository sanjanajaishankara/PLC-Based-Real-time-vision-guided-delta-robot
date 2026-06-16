PROGRAM _CYCLIC

    (* STEP 1: Trigger Pi when robot reaches camera position *)
	IF AtPos1_point1
		AND NOT Trigger_point1
		AND NOT DataReceived_point1
		AND NOT Done_point1 THEN

		Trigger_point1 := TRUE;
		NewDataReady_point1 := FALSE;

	END_IF;


	(* STEP 2: Accept only new Pi data using sequence counter *)
	IF Trigger_point1 AND NOT DataReceived_point1 THEN

		IF SeqCounter1 <> LastSeqCounter1 THEN

			LastSeqCounter1 := SeqCounter1;

			IF ObjCount1 = 0 THEN

				X_Target1 := 0;
				Y_Target1 := 0;

				DataReceived_point1 := TRUE;
				NewDataReady_point1 := TRUE;

			ELSIF ObjCount1 > 0 AND ObjCount1 <= 4 THEN

				X_Target1 := UINT_TO_INT(X_point1);
				Y_Target1 := UINT_TO_INT(Y_point1);

				DataReceived_point1 := TRUE;
				NewDataReady_point1 := TRUE;

			END_IF;

		END_IF;

	END_IF;


	(* STEP 3: Reset after each pick/place cycle *)
	ResetDelay_point1.IN := Done_point1;
	ResetDelay_point1.PT := T#1s;
	ResetDelay_point1();

	IF ResetDelay_point1.Q THEN

		Trigger_point1 := FALSE;
		Done_point1 := FALSE;
		DataReceived_point1 := FALSE;
		NewDataReady_point1 := FALSE;

		ObjCount1 := 0;
		X_Target1 := 0;
		Y_Target1 := 0;

	END_IF;

END_PROGRAM

