VAR CONSTANT
Pos1     : McPointType := (Pos := (X := 0, Y := 0, Z := -432));
SafeZPos : McPointType := (Pos := (X := 0, Y := 0, Z := -340));
Pos2Base : McPointType := (Pos := (X := 0, Y := 0, Z := -330));
PickZPos : REAL := -300;
Pos3     : McPointType := (Pos := (X := 0, Y := 0, Z := -365)); (* PRE_PLACE_LOCATION *)
Pos4     : McPointType := (Pos := (X := 18, Y := 35, Z := -285)); (* PLACE_LOCATION *)

	END_VAR

	VAR
FollowPos : McPointType;
LastPos   : McPointType;
X_cmd     : DINT;
Y_cmd     : DINT;
i         : UDINT;
	END_VAR

	VAR {AT 'Tracking'}
StartTrackingCmd1 : BOOL;
VisionX           : DINT;
VisionY           : DINT;
	END_VAR
	
	VAR {AT 'TeachMode'}
GripperButton1 : BOOL;
	END_VAR


	PROGRAM _MAIN

	Feedrate(5000);

	MoveL(Pos1);
	WaitEndMove();

	MoveL(SafeZPos);
	WaitEndMove();

	StartTrackingCmd1 := TRUE;

	// Tracking loop
	FOR i := 1 TO 20 DO

		X_cmd := VisionX;
		Y_cmd := VisionY;

		FollowPos := Pos2Base;

		// X safety limit
		IF X_cmd > 45 THEN
			FollowPos.Pos.X := 45;
		ELSIF X_cmd < -45 THEN
			FollowPos.Pos.X := -45;
		ELSE
			FollowPos.Pos.X := X_cmd;
		END_IF

		// Y safety limit
		IF Y_cmd > 35 THEN
			FollowPos.Pos.Y := 35;
		ELSIF Y_cmd < -35 THEN
			FollowPos.Pos.Y := -35;
		ELSE
			FollowPos.Pos.Y := Y_cmd;
		END_IF

		FollowPos.Pos.Z := -330;

		MoveL(FollowPos);
		WaitEndMove();

		// Store last valid object position
		LastPos := FollowPos;

		WaitTime(0.1);

	END_FOR

	StartTrackingCmd1 := FALSE;
	
	DO_PATH_SYNCH
	GripperButton1 := TRUE;
	END_PATH_SYNCH


	// Move down at last detected object position
	LastPos.Pos.Z := PickZPos;
	MoveL(LastPos);
	WaitEndMove();

	WaitTime(0.5);
Feedrate(1500);

	// Move back up to safe Z at same X/Y
	LastPos.Pos.Z := -340;
	MoveL(LastPos);
	WaitEndMove();
	
	(* Place *)
	MoveL(Pos3);
	WaitEndMove();

	MoveL(Pos4);
	WaitEndMove();
	
	DO_PATH_SYNCH
	GripperButton1 := FALSE;
	END_PATH_SYNCH


	// Return to home/start position
	MoveL(Pos1);
	WaitEndMove();

	END_PROGRAM

