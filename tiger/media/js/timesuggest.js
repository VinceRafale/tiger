var TimeSuggest = function() {
    this.timeWordMap = {
        "noon": "12:00 PM",
        "midnight": "12:00 AM",
    };
    this.hoursRegex = /^\d{1,2}$/;
    this.hoursAndMinutesRegex = /^(\d{1,2})(?::|\.)([0-5][0-9])$/;
    this.hoursAndMeridianRegex = /^(\d{1,2})\s*(am|a.m|a.m.|pm|p.m|p.m.)$/i;
    this.hoursMinutesAndMeridianRegex = /^(\d{1,2})(?::|\.)([0-5][0-9])\s*(am|a.m|a.m.|pm|p.m|p.m.)$/i;
}

TimeSuggest.prototype = {
    parse: function(str) {
        var now = this.getNow(), orderTime = new Date(), meridian = 'AM', explicitMeridian = false;
        currentHour = now.getHours();
        currentMinutes = now.getMinutes();
        if (this.hoursMinutesAndMeridianRegex.test(str)) {
            bits = this.hoursMinutesAndMeridianRegex.exec(str);
            hour = bits[1];
            minutes = bits[2];
            meridian = bits[3];
            explicitMeridian = true;
        } else if (this.hoursAndMeridianRegex.test(str)) {
            bits = this.hoursAndMeridianRegex.exec(str);
            hour = bits[1];
            minutes = '00';
            meridian = bits[2];
            explicitMeridian = true;
        } else if (this.hoursAndMinutesRegex.test(str)) {
            bits = this.hoursAndMinutesRegex.exec(str);
            hour = bits[1];
            minutes = bits[2];
        } else if (this.hoursRegex.test(str)) {
            hour = this.hoursRegex.exec(str);
            minutes = '00';
        } else if (this.timeWordMap[str]) {
            return this.timeWordMap[str];
        } else {
            return str;
        }
        if (hour > 23) {
            return str;
        }
        if (['am', 'a.m', 'a.m.', 'AM', 'A.M', 'A.M.'].indexOf(meridian) > -1) {
            meridian = 'AM';
        } else {
            meridian = 'PM';
            if (hour < 12) {
                hour = Number(hour) + 12; 
            }
        }
        orderTime.setHours(hour);
        orderTime.setMinutes(minutes);
        // assume they are placing into the future --
        // if order time is less than current time and current time is am,
        // tack another 12 hours to order time so long as they didn't enter am/pm
        if (!explicitMeridian && orderTime.getTime() < now.getTime() && currentHour > 0 && currentHour < 11) {
            hour = Number(hour) + 12; 
        }
        if (!explicitMeridian && hour == 12) {
            meridian = 'PM';
        }
        if (hour > 12) {
            meridian = "PM";
            hour = (hour == 12) ? 12 : hour % 12;
        }
        return hour + ":" + minutes + ' ' + meridian;
    },
    getNow: function() {
        return new Date();
    }
};

(function($){
    $.fn.extend({ 
        timesuggest: function() {
            _timesuggest = new TimeSuggest();
            $(this).blur(function () {
                $(this).val(_timesuggest.parse($(this).val()));
            });
        }
    });
})(jQuery);
