# MFA_Crew
MFA work flow using CrewAI


$ curl -X POST "https://mfa-crew.onrender.com/login"      -H "Content-Type: application/json"      -d '{"user_id": "test_user"}'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    86    0    62  100    24    249     96 --:--:-- --:--:-- --:--:--   351{"message":"\u26a0\ufe0f MFA Required","user_id":"test_user"}

(base)
ravib@DESKTOP-9KU55TH MINGW64 ~/agenticAI (main)
$ curl -X POST "https://mfa-crew.onrender.com/mfa/challenge"      -H "Content-Type: application/json"      -d '{"user_id": "test_user"}'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    82    0    58  100    24    234     97 --:--:-- --:--:-- --:--:--   337{"message":"OTP for test_user is 797942 (Local Testing)"}
