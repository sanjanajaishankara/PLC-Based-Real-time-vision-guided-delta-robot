VAR CONSTANT
Pos1     : McPointType := (Pos := (X := 0,  Y := -0,  Z := -432));
Pos2Base : McPointType := (Pos := (X := 5,  Y := 5,  Z := -285));
Pos3     : McPointType := (Pos := (X := 0, Y := 0, Z := -320)); (* PRE_PLACE_LOCATION *)
Pos4     : McPointType := (Pos := (X := 18, Y := 35, Z := -285)); (* PLACE_LOCATION *)
	END_VAR

	VAR
Pos2        : McPointType;
PosApproach : McPointType;
PosStable   : McPointType;
ObjCountInt : INT;
	END_VAR

	VAR {AT 'PickPlace'}
ObjCount1           : UINT;
X_Target1           : INT;
Y_Target1           : INT;

AtPos1_point1       : BOOL;
Done_point1         : BOOL;
DataReceived_point1 : BOOL;
	END_VAR

	VAR {AT 'TeachMode'}
GripperButton1 : BOOL;
	END_VAR


	PROGRAM _MAIN

	Feedrate(10000);

	WHILE TRUE DO
		
		Feedrate(5000);

		(* Go to camera position *)
		MoveL(Pos1);
		WaitEndMove();

		DO_PATH_SYNCH
		AtPos1_point1 := TRUE;
		END_PATH_SYNCH

		WaitTime(0.5);

		(* Wait for Pi to send N and one pick point *)
		WaitUntil(DataReceived_point1 = TRUE);

		ObjCountInt := UINT_TO_INT(ObjCount1);
		
		DO_PATH_SYNCH
		AtPos1_point1 := FALSE;
		END_PATH_SYNCH

		(* Stop condition: no object remaining *)
		IF ObjCountInt = 0 THEN


			Done_point1 := TRUE;
			WaitUntil(Done_point1 = FALSE);

			EXIT;

		END_IF;

		(* One object pick location *)
		Pos2 := Pos2Base;
		Pos2.Pos.X := X_Target1;
		Pos2.Pos.Y := Y_Target1;

		PosApproach := Pos2;
		PosApproach.Pos.Z := -310;


		(* Move above selected object *)
		MoveL(PosApproach);
		WaitEndMove();
		
		Feedrate(500);

		(* Gripper ON *)
		DO_PATH_SYNCH
		GripperButton1 := TRUE;
		END_PATH_SYNCH

		(* Go down *)
		MoveL(Pos2);
		WaitEndMove();

		WaitTime(1.0);

		(* Lift *)
		MoveL(PosApproach);
		WaitEndMove();
		
		Feedrate(500);

		(* Place *)
		MoveL(Pos3);
		WaitEndMove();

		MoveL(Pos4);
		WaitEndMove();

		(* Release *)
		DO_PATH_SYNCH
		GripperButton1 := FALSE;
		END_PATH_SYNCH

		WaitTime(1.0);
		

		(* Tell Pi this one object cycle is complete *)
		Done_point1 := TRUE;

		(* Wait until cyclic program resets Done/DataReceived/Trigger *)
		WaitUntil(Done_point1 = FALSE);

	END_WHILE;

	END_PROGRAM

