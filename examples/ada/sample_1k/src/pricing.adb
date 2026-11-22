package body PriceRule_Service is

   -- Compute pricing score variant 1
   function Compute_PriceRule_Score_1 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 3;
      elsif Tier = 2 then
         Result := Result + 2;
      end if;
      return Result + 1;
   end Compute_PriceRule_Score_1;

   -- Compute pricing score variant 2
   function Compute_PriceRule_Score_2 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 6;
      elsif Tier = 2 then
         Result := Result + 4;
      end if;
      return Result + 2;
   end Compute_PriceRule_Score_2;

   -- Compute pricing score variant 3
   function Compute_PriceRule_Score_3 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 9;
      elsif Tier = 2 then
         Result := Result + 6;
      end if;
      return Result + 3;
   end Compute_PriceRule_Score_3;

   -- Compute pricing score variant 4
   function Compute_PriceRule_Score_4 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 12;
      elsif Tier = 2 then
         Result := Result + 8;
      end if;
      return Result + 4;
   end Compute_PriceRule_Score_4;

   -- Compute pricing score variant 5
   function Compute_PriceRule_Score_5 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 15;
      elsif Tier = 2 then
         Result := Result + 10;
      end if;
      return Result + 5;
   end Compute_PriceRule_Score_5;

   -- Compute pricing score variant 6
   function Compute_PriceRule_Score_6 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 18;
      elsif Tier = 2 then
         Result := Result + 12;
      end if;
      return Result + 6;
   end Compute_PriceRule_Score_6;

   -- Compute pricing score variant 7
   function Compute_PriceRule_Score_7 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 21;
      elsif Tier = 2 then
         Result := Result + 14;
      end if;
      return Result + 7;
   end Compute_PriceRule_Score_7;

   -- Compute pricing score variant 8
   function Compute_PriceRule_Score_8 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 24;
      elsif Tier = 2 then
         Result := Result + 16;
      end if;
      return Result + 8;
   end Compute_PriceRule_Score_8;

   -- Compute pricing score variant 9
   function Compute_PriceRule_Score_9 (Qty : Integer; Tier : Integer) return Integer is
      Result : Integer := Qty * 10;
   begin
      if Qty <= 0 then
         return 0;
      end if;
      if Tier >= 3 then
         Result := Result + 27;
      elsif Tier = 2 then
         Result := Result + 18;
      end if;
      return Result + 9;
   end Compute_PriceRule_Score_9;

end PriceRule_Service;
