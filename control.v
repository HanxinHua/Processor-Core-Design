// Control for the Duke 550 Processor
// Authors: <A, B and C>

	module control ( 	input [4:0] op,
						// TODO: Figure out what other control signals you require for your processor						
						// TODO: Figure out what values they will take based on the opcode
						output  BR, JP, ALUinB, DMwe, Rwe, Rdst, Rwd,JAL,JR,BGT ,input_ack,LCD_wren,
						output [2:0] ALUop
						);

// Hint: This unit basically decides the values of the control signals
// based on the input opcode received. Eg. Look at slide 31 in Lecture 9

assign	BR=(op[4:0]==5'b01001)?1'b1:1'b0;

assign  BGT=(op[4:0]==5'b01010)?1'b1:1'b0; 

assign  JR=(op[4:0]==5'b01011)?1'b1:1'b0; 

assign  JAL=(op[4:0]==5'b01101)?1'b1:1'b0; 

assign  input_ack=(op[4:0]==5'b01110)?1'b1:1'b0; 

assign  LCD_wren=(op[4:0]==5'b01111)?1'b1:1'b0; 

assign  JP=	(op[4:0]==5'b01100)?1'b1:
				(op[4:0]==5'b01101)?1'b1:1'b0;

assign  ALUinB=(op[4:0]==5'b00110)?1'b1:
		   		(op[4:0]==5'b00111)?1'b1:
				(op[4:0]==5'b01000)?1'b1:1'b0;

assign	DMwe=(op[4:0]==5'b01000)?1'b1:1'b0;

assign  Rwe =(op[4:0]==5'b01000)?1'b0:
		   	(op[4:0]==5'b01001)?1'b0:
		   	(op[4:0]==5'b01010)?1'b0:
		   	(op[4:0]==5'b01011)?1'b0:
		   	(op[4:0]==5'b01100)?1'b0:
			(op[4:0]==5'b01111)?1'b0:1'b1;

assign  Rdst=(op[4:0]==5'b00000)?1'b1:
		   		(op[4:0]==5'b00001)?1'b1:
		   		(op[4:0]==5'b00010)?1'b1:
		   		(op[4:0]==5'b00011)?1'b1:
		   		(op[4:0]==5'b00100)?1'b1:
		   		(op[4:0]==5'b00101)?1'b1:1'b0;
				//(op[4:0]==5'b01111)?1'b1:1'b0;

assign	Rwd=(op[4:0]==5'b00111)?1'b1:1'b0;


assign  ALUop=(op[4:0]==5'b00001)?3'b001:
  			  (op[4:0]==5'b00010)?3'b010:
  			  (op[4:0]==5'b00011)?3'b011:
  			  (op[4:0]==5'b00100)?3'b100:
  			  (op[4:0]==5'b00101)?3'b101:
  			  (op[4:0]==5'b01010)?3'b001:
  			  (op[4:0]==5'b01001)?3'b001:3'b0;



endmodule 