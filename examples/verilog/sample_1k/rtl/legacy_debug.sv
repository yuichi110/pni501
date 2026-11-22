module legacy_debug(input logic clk);
    always_ff @(posedge clk) begin
        $display("debug tick");
    end
endmodule
