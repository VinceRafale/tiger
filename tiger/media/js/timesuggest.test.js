$(document).ready(function(){
    test("Conversion of time words", function() {
        timesuggest = new TimeSuggest();
        equals(timesuggest.parse("midnight"), "12:00 AM");
        equals(timesuggest.parse("noon"), "12:00 PM");
    });
    test("Hours without minutes or meridian", function() {
        timesuggest = new TimeSuggest();
        now = new Date();
        now.setHours(8);
        now.setMinutes(0);
        new Smoke.Stub(timesuggest, "getNow").and_return(now);
        equals(timesuggest.parse("5"), "5:00 PM", "Current time should be 12 hours in advance if current time is AM");
        equals(timesuggest.parse("6"), "6:00 PM", "Current time should be 12 hours in advance if current time is AM");
        equals(timesuggest.parse("7"), "7:00 PM", "Current time should be 12 hours in advance if current time is AM");
        equals(timesuggest.parse("8"), "8:00 AM");
        equals(timesuggest.parse("9"), "9:00 AM");
        equals(timesuggest.parse("10"), "10:00 AM");
        equals(timesuggest.parse("11"), "11:00 AM");
        equals(timesuggest.parse("12"), "12:00 PM");
        equals(timesuggest.parse("13"), "1:00 PM");
        equals(timesuggest.parse("14"), "2:00 PM");
        equals(timesuggest.parse("15"), "3:00 PM");
        equals(timesuggest.parse("16"), "4:00 PM");
        equals(timesuggest.parse("17"), "5:00 PM");
        equals(timesuggest.parse("18"), "6:00 PM");
        equals(timesuggest.parse("19"), "7:00 PM");
        equals(timesuggest.parse("20"), "8:00 PM");
        equals(timesuggest.parse("21"), "9:00 PM");
        equals(timesuggest.parse("22"), "10:00 PM");
        equals(timesuggest.parse("23"), "11:00 PM");
    });
    test("Hours with meridian -- all formats", function() {
        timesuggest = new TimeSuggest();
        now = new Date();
        now.setHours(8);
        now.setMinutes(0);
        new Smoke.Stub(timesuggest, "getNow").and_return(now);
        equals(timesuggest.parse("10 am"), "10:00 AM");
        equals(timesuggest.parse("10 a.m"), "10:00 AM");
        equals(timesuggest.parse("10 a.m."), "10:00 AM");
        equals(timesuggest.parse("10 AM"), "10:00 AM");
        equals(timesuggest.parse("10 A.M."), "10:00 AM");
        equals(timesuggest.parse("10 pm"), "10:00 PM");
        equals(timesuggest.parse("10 p.m"), "10:00 PM");
        equals(timesuggest.parse("10 p.m."), "10:00 PM");
        equals(timesuggest.parse("10 PM"), "10:00 PM");
        equals(timesuggest.parse("10 P.M."), "10:00 PM");
    });
    test("Hours with minutes", function() {
        timesuggest = new TimeSuggest();
        now = new Date();
        now.setHours(8);
        now.setMinutes(0);
        new Smoke.Stub(timesuggest, "getNow").and_return(now);
        equals(timesuggest.parse("5:30"), "5:30 PM", "Current time should be 12 hours in advance if current time is AM");
        equals(timesuggest.parse("6:30"), "6:30 PM", "Current time should be 12 hours in advance if current time is AM");
        equals(timesuggest.parse("7:30"), "7:30 PM", "Current time should be 12 hours in advance if current time is AM");
        equals(timesuggest.parse("8:30"), "8:30 AM");
        equals(timesuggest.parse("9:30"), "9:30 AM");
        equals(timesuggest.parse("10:30"), "10:30 AM");
        equals(timesuggest.parse("11:30"), "11:30 AM");
        equals(timesuggest.parse("12:30"), "12:30 PM");
        equals(timesuggest.parse("13:30"), "1:30 PM");
        equals(timesuggest.parse("14:30"), "2:30 PM");
        equals(timesuggest.parse("15:30"), "3:30 PM");
        equals(timesuggest.parse("16:30"), "4:30 PM");
        equals(timesuggest.parse("17:30"), "5:30 PM");
        equals(timesuggest.parse("18:30"), "6:30 PM");
        equals(timesuggest.parse("19:30"), "7:30 PM");
        equals(timesuggest.parse("20:30"), "8:30 PM");
        equals(timesuggest.parse("21:30"), "9:30 PM");
        equals(timesuggest.parse("22:30"), "10:30 PM");
        equals(timesuggest.parse("23:30"), "11:30 PM");
    });
    test("Hours with minutes and meridian", function() {
        timesuggest = new TimeSuggest();
        now = new Date();
        now.setHours(8);
        now.setMinutes(0);
        new Smoke.Stub(timesuggest, "getNow").and_return(now);
        for (i = 1; i <= 12; i++) {
            amTime = i + ":30 am";
            equals(timesuggest.parse(amTime), amTime.toUpperCase());
            pmTime = i + ":30 pm";
            equals(timesuggest.parse(pmTime), pmTime.toUpperCase());
        }
    });
});

