module processor ( 	input clock,
							input reset,
							input [31:0] keyboard_in,
							output keyboard_ack, 
							output lcd_write,
							output [31:0] lcd_data
							);

// The core of the Duke 550 processor
// Author: <Mengxi Wu><Hanxin Hua><Liwen Deng>


// Define all the wires you will need below:
wire [11:0] pc,add_one,pc_one,pc_br,br_out,jp_out,q_i_add,add_zero,jr_out;
wire [31:0] data, pc_one_ext;
wire [31:0] q_i, q_d;
wire BR, BGT, JP, JAL, JR, ALUinB, DMwe, Rwe, Rdst, Rwd, input_ack, LCD_wren, br_sig, isEqual, isLessThan;
wire [2:0] ALUop;
wire [4:0]  r31;
wire [16:0] imme;
wire [4:0] rdst_out1,rdst_out2,rt_out;
wire [31:0] A_val, B_val,aluinb_out,alu_out, rwd_out, rd_jal_out, rd_input_out;
wire [31:0] imme_ext, target;
wire [4:0] op, rs, rt, rd;
wire zero,one;
wire [31:0] a;




// Instantiate the imem - connect with wires to other units?
imem my_imem (.address(q_i_add), .clken(one), .clock(clock), .q(q_i));

// Instantiate the dmem - connect with wires to other units?
dmem my_dmem (.address(alu_out[11:0]), .clock(~clock), .data(B_val), .wren(DMwe), .q(q_d));

// Instantiate the regfile - connect with wires to other units?
regfile my_reg (.clock(clock), .wren(Rwe), .clear(reset), .regD(rdst_out2), .regA(rs), .regB(rdst_out1), .valD(rd_input_out), .valA(A_val), .valB(B_val));

// Instantiate the alu - connect with wires to other units?
alu my_alu (.A(A_val), .B(aluinb_out), .op(ALUop), .R(alu_out), .isEqual(isEqual), .isLessThan(isLessThan));

// Instantiate the control unit - connect with with wires to other units?
control my_control (.op(op), .BR(BR),.BGT(BGT),  .JR(JR), .JAL(JAL),  .JP(JP), .ALUinB(ALUinB), .DMwe(DMwe), .Rwe(Rwe), .Rdst(Rdst), .Rwd(Rwd), .ALUop(ALUop), .input_ack(input_ack), .LCD_wren(LCD_wren));

adder_cs#(12) adder_pc (.A(add_one), .B(pc), .cin(zero), .cout(), .sum(pc_one), .signed_overflow());

adder_cs#(12) adder_br (.A(pc_one), .B(imme_ext[11:0]), .cin(zero), .cout(), .sum(pc_br), .signed_overflow());

//lcd my_lcd (.clock(clock),.reset(reset),.write_en(LCD_wren),.data(a[7:0]),.lcd_data(lcd_data[7:0]), .lcd_rw(),.lcd_en(),.lcd_rs(),.lcd_on(),.lcd_blon());

//ps2 keyboard (clock,reset,acknowledge,ps2_clock,ps2_data,);

mux#(5) mux_rdst (.A(rd), .B(rt), .s(Rdst), .F(rdst_out1));

mux#(32) mux_aluinb (.A(B_val), .B(imme_ext), .s(ALUinB), .F(aluinb_out));

mux#(32) mux_rwd (.A(alu_out), .B(q_d), .s(Rwd), .F(rwd_out));

mux#(12) mux_br (.A(pc_one), .B(pc_br), .s(br_sig), .F(br_out));

mux#(12) mux_jp (.A(br_out), .B(target[11:0]), .s(JP), .F(jp_out));

mux#(12) mux_jr (.A(jp_out), .B(B_val[11:0]), .s(JR), .F(jr_out));

mux#(5) mux_jal (.A(rd), .B(r31), .s(JAL), .F(rdst_out2));

//mux mux_rt (.A(rt), .B(rd), .s(JR), .F(rt_out));

mux#(32) mux_rd_jal (.A(rwd_out), .B(pc_one_ext), .s(JAL), .F(rd_jal_out));

mux#(32) mux_input_out (.A(rd_jal_out), .B(keyboard_in), .s(input_ack), .F(rd_input_out));

mux#(12) mux_reset (.A(jr_out), .B(add_zero), .s(reset), .F(q_i_add));

reg_new#(12) PC (.D(jr_out), .clock(clock), .clear(reset), .enable(one), .Q(pc));
/* TODO: Connect stuff up to make a processor*/

	
	//FETCH Stage
assign a=32'b00000000000000000000000001100001;
assign zero=0;
assign one=1;
assign add_zero=12'b000000000000;
assign op=q_i[31:27];
assign rd=q_i[26:22];
assign rs=q_i[21:17];
assign rt=q_i[16:12];
assign imme=q_i[16:0];
assign target[26:0]=q_i[26:0];
assign target[31:27]=5'b00000;
assign r31=5'b11111;
assign pc_one_ext[11:0]=pc_one;
assign pc_one_ext[31:12]=0;
assign add_one=12'b000000000001;
assign imme_ext[16:0]=imme;
assign imme_ext[31:17]=(imme[16]==1'b0)?15'b000000000000000:15'b111111111111111; 
assign keyboard_ack=input_ack;
assign lcd_write=LCD_wren;
assign br_sig=((BR & isEqual) | (BGT & isLessThan));

assign lcd_data[7:0]=B_val[7:0];

	

endmodule
