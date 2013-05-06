
var timeDelay = 5 * 60 * 1000; //5 mins
      
$.widget( "ui.timespinner", $.ui.spinner, {
  options: {
    // seconds
    step: 60 * 1000,
    // hours
    page: 60
  },
  _parse: function( value ) {
    if ( typeof value === "string" ) {
      // already a timestamp
      if ( Number( value ) == value ) {
        return Number( value );
      }
      return +Globalize.parseDate( value );
    }
    return value;
  },
  _format: function( value ) {
    return Globalize.format( new Date(value), "t" );
  }
});

$(function() {
  $( "#jobListDateRange" ).hide();
  
  $( "#jobsFrom" ).datepicker({
    defaultDate: "-1",
    changeMonth: true,
    numberOfMonths: 2,
    dateFormat: "yy-mm-dd",
    onClose: function( selectedDate ) {
      $( "#jobsTo" ).datepicker( "option", "minDate", selectedDate );
    }
  });

  $( "#jobsTo" ).datepicker({
    defaultDate: "+7",
    changeMonth: true,
    numberOfMonths: 2,
    dateFormat: "yy-mm-dd",
    onClose: function( selectedDate ) {
      $( "#jobsFrom" ).datepicker( "option", "maxDate", selectedDate );
    }

  });
  
  $( "#jobsFrom" ).datepicker("setDate",-1);
  $( "#jobsTo" ).datepicker("setDate",30);
  
//   Globalize.culture( "de-DE" );
});

function populatePanes() 
{
  var fromDate = $("#jobsFrom").datepicker('getDate');
  var fromEpoch = fromDate.getTime()/1000.0;

  var toDate = $("#jobsTo").datepicker('getDate');
  //add a day - want everything up to the end of midnight
  //on the to date
  toDate.setDate(toDate.getDate()+1);
  var toEpoch = toDate.getTime()/1000.0;

  $("#jobCandidates").html( "" );
  // get images from the db
  $.ajax({
    url: "../image",
    dataType: 'json',
    async: false,
    data: {jobList: 0,
     status: "pending"},
    success: function(json) {
      $.each(json, function (e, y) {
        var li = createImageListElement(y);
        //#0:image ID, 1:image URL, 2:status, 3:jobtime, 4:unixtime
        li.attr("jobTime",y[3]);
        li.attr("unixTime",y[4]);
        li.attr("candidate",true);
        $( "#jobCandidates").append(li);
      });
    }
  });

  $.ajax({
    url: "../image",
    dataType: 'json',
    async: false,
    data: {jobList: 0,
     status: "queued",
     minDate: fromEpoch,
     maxDate: toEpoch},
    success: function(json) {
      $.each(json, function (e, y) {
        var li = createImageListElement(y);
        //#0:image ID, 1:image URL, 2:status, 3:jobtime, 4:unixtime
        li.attr("jobTime",y[3]);
        li.attr("unixTime",y[4]);
        li.attr("candidate",false);
        $( "#jobQueued").append(li);
      });
    }
  });

}

function setupCalendar()
{
  var fromDate = $("#jobsFrom").datepicker('getDate');
  var toDate = $("#jobsTo").datepicker('getDate');
  $("#jobQueued").html( "" );

  while (fromDate < toDate)
  {
    var hour = 2;
    var minute = 0;
    var dayDate = new Date(fromDate);
    var day = dayDate.getDate();
    var month = dayDate.getMonth();
    var year = dayDate.getFullYear();
    var displayId = day + "/" + (month+1) + "/" + year;
    var id = day + "_" + month + "_" + year;
    
    var li = $('<li>');
    li.attr("class","fixed dateHeader");
    li.attr("hour", hour);
    li.attr("minute", minute);
    li.attr("day", day);
    li.attr("month", month);
    li.attr("year", year);
    var unixTime =  dayDate.getTime() / 1000.0;
    li.attr("jobTime", unixTime); 
    li.append(displayId);
    li.append('<br/>');
    
    $("#jobQueued").append(li);    

    fromDate.setDate(fromDate.getDate()+1);
  }
  
}

function commitJobs()
{
  var nQueued = 0;
  var currDate = new Date();
  var initialised = false;
  
  $("#jobQueued li").each (function (index, li) {
    if ($(this).hasClass("fixed") == false)
    {
      var dbid = jQuery(this).find("img").attr("dbid");
      var status = 'queued';
      var timeStamp = jQuery(this).attr("jobTime");
      
      submitDict = {}
      submitDict["queueJob"] = 0;
      submitDict["imageId"] = dbid;
      submitDict["status"] = status;
      submitDict["jobTime"] = timeStamp;
      
      $.ajax({
        type: 'POST',
        url: "../image",
        dataType: 'json',
        async: false,
        data: submitDict,
        success: function(json) {
          return true
        }
      }); 
    }
  });
  
  $("#jobCandidates li").each (function (index, li) {
    var dbid = jQuery(this).find("img").attr("dbid");
    var candidate = jQuery(this).attr("candidate");
    
    submitDict = {}
    submitDict["queueJob"] = 0;
    submitDict["imageId"] = dbid;
    submitDict["status"] = "pending";
    submitDict["jobTime"] = 0;
    
    if (candidate == "false")
    {
      $.ajax({
        type: 'POST',
        url: "../image",
        dataType: 'json',
        async: false,
        data: submitDict,
        success: function(json) {
          return true
        }
      });
    }
  });
}

$("#jobsApplyButton").click(function () {
  commitJobs();
  showMain();
});

$("#jobsDatesButton").click(function () {
  setupJobsPane();
});

function getJobQueueTime(startIndex) 
{
  for (var i = startIndex - 1; i >= 0; i--)
  {
    var li = $("#jobQueued li").eq(i);
    var time = li.attr("jobTime");
    time = parseInt(time) + parseInt(timeDelay/1000);
    return time;
  }
}

function setupJobsPane()
{
  setupCalendar();
  populatePanes();  

  var jobQueuedList = $('#jobQueued');
  var listitems = jobQueuedList.children('li').get();
  listitems.sort(function(a, b) {
    var aAttr = $(a).attr("jobTime");
    var bAttr = $(b).attr("jobTime"); 
    return (parseInt(aAttr)>parseInt(bAttr)) ? 1 : -1;
  });
  $.each(listitems, function(idx, itm) { jobQueuedList.append(itm); });

  var jobCandidatesList = $('#jobCandidates');
  var listitems = jobCandidatesList.children('li').get();
  listitems.sort(function(a, b) {
    var aAttr = $(a).attr("unixTime");
    var bAttr = $(b).attr("unixTime"); 
    return (parseInt(aAttr)<parseInt(bAttr)) ? 1 : -1;
  });
  $.each(listitems, function(idx, itm) { jobCandidatesList.append(itm); });
  
  $( "#jobCandidates, #jobQueued" ).sortable({
    connectWith: ".connectedSortable",
    cancel: ".fixed"
  }).disableSelection();

  $('#jobQueued').droppable({
    drop: function (ev, ui) {
      // get index of empty spot to drag into
      var i = $("#jobQueued .ui-sortable-placeholder").index();
      var time = getJobQueueTime(i);
      var droppedElem = $(ui.draggable);
      droppedElem.attr("jobTime", time);
      
      //add or update queued corner tag
      if (droppedElem.hasClass('queued'))
      {
        droppedElem.find(".jobTimeStamp").text(timestampToDate(time));
      }
      else
      {
        var queuedTag = $('<div>');
        queuedTag.addClass('queuedTag');
        queuedTag.appendTo(droppedElem);
        var jobTime = $('<span>');
        jobTime.addClass('jobTimeStamp');
        jobTime.text(timestampToDate(time));
        jobTime.appendTo(droppedElem);
      }
      
      droppedElem.addClass('queued');
    }
  });
  
  $('#jobCandidates').droppable({
    drop: function (ev, ui) {
      var droppedElem = $(ui.draggable);
      droppedElem.children('.queuedTag').remove();
      droppedElem.children('.jobTimeStamp').remove();
      droppedElem.removeClass('queued');
    }
  });
}

$( "#jobListDateRangeShow" ).click(function() {
  $("#jobListDateRangeShow").hide("fast");
  $("#jobListDateRange").show("fast");
});

$( "#jobListDateRangeHide" ).click(function() {
  $("#jobListDateRange").hide("fast");
  $("#jobListDateRangeShow").show("fast");
});
