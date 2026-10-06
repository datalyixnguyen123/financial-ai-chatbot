
 ================================================================================
M6.5 — ERROR ANALYSIS
================================================================================

--------------------------------------------------------------------------------
TEST 1
TEXT: Nay ăn phở 50k

Expected:
  AMOUNT             -> 50k

Predicted:
  AMOUNT             -> 50k

STATUS: PASS

--------------------------------------------------------------------------------
TEST 2
TEXT: Tôi muốn tiết kiệm 30 triệu trong 6 tháng

Expected:
  TARGET_AMOUNT      -> 30 triệu
  DURATION           -> 6 tháng

Predicted:
  TARGET_AMOUNT      -> 30 triệu
  DURATION           -> 6 tháng

STATUS: PASS

--------------------------------------------------------------------------------
TEST 3
TEXT: Cho giải trí tối đa 700k mỗi tháng

Expected:
  BUDGET_LIMIT       -> 700k
  PERIOD             -> mỗi tháng

Predicted:
  TARGET_AMOUNT      -> 700k
  PERIOD             -> mỗi tháng

Invalid BIO transitions:
  position=7 | B-TARGET_AMOUNT -> I-BUDGET_LIMIT | I-ENTITY type mismatch

STATUS: ERROR

--------------------------------------------------------------------------------
TEST 4
TEXT: Mẹ chuyển khoản cho mình 1 triệu

Expected:
  PAYMENT_METHOD     -> chuyển khoản
  AMOUNT             -> 1 triệu

Predicted:
  AMOUNT             -> 1 triệu

STATUS: ERROR

--------------------------------------------------------------------------------
TEST 5
TEXT: Grab hôm nay 65k

Expected:
  MERCHANT           -> Grab
  AMOUNT             -> 65k

Predicted:
  AMOUNT             -> 65k

STATUS: ERROR

--------------------------------------------------------------------------------
TEST 6
TEXT: Cho tôi ngân sách ăn uống tối đa 2 triệu mỗi tháng

Expected:
  BUDGET_LIMIT       -> 2 triệu
  PERIOD             -> mỗi tháng

Predicted:
  TARGET_AMOUNT      -> 2 triệu
  PERIOD             -> mỗi tháng

STATUS: ERROR

--------------------------------------------------------------------------------
TEST 7
TEXT: Ngân sách cho việc đi lại mỗi tháng là 1 triệu

Expected:
  BUDGET_LIMIT       -> 1 triệu
  PERIOD             -> mỗi tháng

Predicted:
  PERIOD             -> mỗi tháng
  TARGET_AMOUNT      -> 1 triệu

STATUS: ERROR


================================================================================
SUMMARY
================================================================================

  
    

    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }


  
    
      
      test
      text
      status
      expected_types
      predicted_types
      missed
      extra
      invalid_bio
    

    
      0
      1
      Nay ăn phở 50k
      PASS
      AMOUNT
      AMOUNT
      
      
      0
    
    
      1
      2
      Tôi muốn tiết kiệm 30 triệu trong 6 tháng
      PASS
      DURATION, TARGET_AMOUNT
      DURATION, TARGET_AMOUNT
      
      
      0
    
    
      2
      3
      Cho giải trí tối đa 700k mỗi tháng
      ERROR
      BUDGET_LIMIT, PERIOD
      PERIOD, TARGET_AMOUNT
      BUDGET_LIMIT
      TARGET_AMOUNT
      1
    
    
      3
      4
      Mẹ chuyển khoản cho mình 1 triệu
      ERROR
      AMOUNT, PAYMENT_METHOD
      AMOUNT
      PAYMENT_METHOD
      
      0
    
    
      4
      5
      Grab hôm nay 65k
      ERROR
      AMOUNT, MERCHANT
      AMOUNT
      MERCHANT
      
      0
    
    
      5
      6
      Cho tôi ngân sách ăn uống tối đa 2 triệu mỗi t...
      ERROR
      BUDGET_LIMIT, PERIOD
      PERIOD, TARGET_AMOUNT
      BUDGET_LIMIT
      TARGET_AMOUNT
      0
    
    
      6
      7
      Ngân sách cho việc đi lại mỗi tháng là 1 triệu
      ERROR
      BUDGET_LIMIT, PERIOD
      PERIOD, TARGET_AMOUNT
      BUDGET_LIMIT
      TARGET_AMOUNT
      0


================================================================================
ERROR GROUPS
================================================================================
TEST 3: missed=[BUDGET_LIMIT] extra=[TARGET_AMOUNT] invalid_bio=1
TEST 4: missed=[PAYMENT_METHOD] extra=[] invalid_bio=0
TEST 5: missed=[MERCHANT] extra=[] invalid_bio=0
TEST 6: missed=[BUDGET_LIMIT] extra=[TARGET_AMOUNT] invalid_bio=0
TEST 7: missed=[BUDGET_LIMIT] extra=[TARGET_AMOUNT] invalid_bio=0


================================================================================
M6.5 DIAGNOSTIC
================================================================================

1. AMOUNT:
   Strong on tested examples.

2. DURATION:
   Strong on tested examples.

3. PERIOD:
   Strong on tested examples.

4. TARGET_AMOUNT:
   Generally recognized, but may be confused with BUDGET_LIMIT.

5. BUDGET_LIMIT:
   Main semantic weakness.
   Context such as "ngân sách", "tối đa", "giới hạn"
   is not always sufficient for the current NER model.

6. MERCHANT:
   Frequently missed.
   Training support is very small.

7. PAYMENT_METHOD:
   Frequently missed.
   Training support is very small.

8. BIO RECONSTRUCTION:
   Invalid transitions such as
   B-TARGET_AMOUNT -> I-BUDGET_LIMIT
   must not be interpreted as two independent entities.

M6.5 COMPLETE


