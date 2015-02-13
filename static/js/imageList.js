//
//  Copyright (c) 2013 Bhautik J Joshi (bjoshi@gmail.com)
// 
//  Permission is hereby granted, free of charge, to any person obtaining a copy
//  of this software and associated documentation files (the "Software"), to deal
//  in the Software without restriction, including without limitation the rights
//  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//  copies of the Software, and to permit persons to whom the Software is
//  furnished to do so, subject to the following conditions:
// 
//  The above copyright notice and this permission notice shall be included in
//  all copies or substantial portions of the Software.
// 
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
//  THE SOFTWARE.
//

$(function() {
  $("#imageListFilter").hide();
  $("#imageListUtility").hide();
  
  $( "#from" ).datepicker({
    defaultDate: "+1w",
    changeMonth: true,
    numberOfMonths: 2,
    dateFormat: "yy-mm-dd",
    onClose: function( selectedDate ) {
      $( "#to" ).datepicker( "option", "minDate", selectedDate );
    }
  });
  $( "#to" ).datepicker({
    defaultDate: "+1w",
    changeMonth: true,
    numberOfMonths: 2,
    dateFormat: "yy-mm-dd",
    onClose: function( selectedDate ) {
      $( "#from" ).datepicker( "option", "maxDate", selectedDate );
    }
  });
});

$(function() {
  $( "#dbImageList" ).selectable();
  refreshImages($( "#dbImageList" ));
});

function timestampToDate(stamp)
{

  var date = new Date(stamp*1000);
//   var hours = date.getHours();
//   var minutes = date.getMinutes();
//   var seconds = date.getSeconds();
//   
//   var year = date.getFullYear();
//   var month = date.getMonth() + 1;
//   var date = date.getDate();
// 
//   var formattedTime = hours + ':' + minutes + ':' + seconds;
//   var formattedDate = date + '/' + month + '/' + year;
//   
//   return formattedTime + ' ' + formattedDate; 
  return date.toLocaleString("en-GB");
}

// #0:dbid
// #1:src
// #2:status
// #3:jobtime
// #4:unixtime

function createImageListElement(data)
{
  var li = $('<li>');
  li.attr('class','ui-widget-content')
  li.addClass(data[2]);
  
  if (data[2] == 'queued')
  {
    if (data[3] != 0)
    {
      createTimeTag(data[3], li);
    }
  }

  var img = $('<img id="dynamic">');
  img.attr('src', data[1] + '.thumb.jpg');
  img.attr('dbid',data[0]);
  img.appendTo(li);

  return li;
}

function createTimeTag(timeStamp, liElem)
{
  var date = new Date(timeStamp*1000);
  var dt = $.datepicker.formatDate('yy-mm-dd', date);
  
  var queuedTag = $('<div>');
  queuedTag.addClass('queuedTag');
  queuedTag.appendTo(liElem);
  
  var jobTimeLabel = $('<span>');
  jobTimeLabel.addClass('jobTimeStamp');
  jobTimeLabel.text(timestampToDate(timeStamp));
  jobTimeLabel.appendTo(liElem);
  
  var jobTime = $('<input/>');
//   jobTime.addClass('jobTimeStamp');
  jobTime.addClass('jobTimePicker');
  jobTime.attr('value',"");
  jobTime.attr('type','text');
  jobTime.datetimepicker({ 
    showOn: "both",
    onClose: function( selectedDate ) {
      var newDate = jobTime.datepicker('getDate') / 1000;
      liElem.attr("jobTime", newDate);
      jobTimeLabel.text(timestampToDate(newDate));
      
      var candidate = liElem.attr("candidate");
      if (candidate == undefined)
      {
        postQueuedJob(liElem);
      }
      else
      {
        sortJobItems();
      }
    }
  });
  
  jobTime.datepicker('setDate', date);
  jobTime.appendTo(liElem);
  
  jobTime.hide();
  queuedTag.click(function () {
    jobTime.datepicker('show');
  });
  
  jobTimeLabel.click(function () {
    jobTime.datepicker('show');
  });
  

}

$( "#applyFilterButton" ).click(function() {
  var fromDate = $("#from").datepicker('getDate');
  var fromEpoch = fromDate.getTime()/1000.0;
  var toDate = $("#to").datepicker('getDate');
  //add a day - want everything up to the end of midnight
  //on the to date
  toDate.setDate(toDate.getDate()+1);
  var toEpoch = toDate.getTime()/1000.0;
  $( "#dbImageList" ).html( "" );

  // get images from the db
  $.ajax({
    url: "../image",
    dataType: 'json',
    async: false,
    data: {imageList: 0,
     minDate: fromEpoch,
     maxDate: toEpoch},
    success: function(json) {
      $.each(json, function (e, y) {
        var li = createImageListElement(y);
        $('#dbImageList').append(li);
      });
    } 
  });

  $("#imageListFilter").hide("fast");
  $("#imageListFilterButton").show("fast");
});

function refreshImages(listElement)
{
  listElement.html( "" );
  // get images from the db
  $.ajax({
    url: "../image",
    dataType: 'json',
    async: false,
    data: {imageList: 0},
    success: function(json) {
      $.each(json, function (e, y) {
        var li = createImageListElement(y);
        listElement.append(li);
      });
    } 
  });

  // get the min/max date range
  $.ajax({
    url: "../image",
    dataType: 'json',
    async: false,
    data: {getImageDateRange: 0},
    success: function(json) {
      var minEpoch = new Date(json[0]*1000);
      var maxEpoch = new Date(json[1]*1000);
      $("#from").datepicker('setDate', minEpoch);
      $("#to").datepicker('setDate', maxEpoch);
    } 
  });
}

$( "#imageListFilterButton" ).click(function() {
  $("#imageListFilterButton").hide("fast");
  $("#imageListFilter").show("fast");
});

$( "#imageListFilterHide" ).click(function() {
  $("#imageListFilter").hide("fast");
  $("#imageListFilterButton").show("fast");
});


$( "#imageListUtilityShow" ).click(function() {
  $("#imageListUtilityShow").hide("fast");
  $("#imageListUtility").show("fast");
});

$( "#imageListUtilityHide" ).click(function() {
  $("#imageListUtility").hide("fast");
  $("#imageListUtilityShow").show("fast");
});