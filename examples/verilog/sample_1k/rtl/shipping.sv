// Shipment ALU stage 1
module shipment_stage_1(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd3;
        end else begin
            score = qty + 16'd1;
        end
    end
endmodule

// Shipment ALU stage 2
module shipment_stage_2(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd6;
        end else begin
            score = qty + 16'd2;
        end
    end
endmodule

// Shipment ALU stage 3
module shipment_stage_3(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd9;
        end else begin
            score = qty + 16'd3;
        end
    end
endmodule

// Shipment ALU stage 4
module shipment_stage_4(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd12;
        end else begin
            score = qty + 16'd4;
        end
    end
endmodule

// Shipment ALU stage 5
module shipment_stage_5(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd15;
        end else begin
            score = qty + 16'd5;
        end
    end
endmodule

// Shipment ALU stage 6
module shipment_stage_6(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd18;
        end else begin
            score = qty + 16'd6;
        end
    end
endmodule

// Shipment ALU stage 7
module shipment_stage_7(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd21;
        end else begin
            score = qty + 16'd7;
        end
    end
endmodule

// Shipment ALU stage 8
module shipment_stage_8(
    input logic [15:0] qty,
    input logic [1:0] tier,
    output logic [15:0] score
);
    always_comb begin
        if (qty == 16'd0) begin
            score = 16'd0;
        end else if (tier == 2'd3) begin
            score = qty + 16'd24;
        end else begin
            score = qty + 16'd8;
        end
    end
endmodule
