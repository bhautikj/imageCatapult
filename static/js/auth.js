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

var jsonAuthUrl = "../auth";

$(function() {
  $("#flickrAppInput").hide();
  $("#facebookAppInput").hide();
  $("#tumblrAppInput").hide();
  $("#twitterAppInput").hide();
  onAuthShow();  
});


function onAuthShow()
{
    $.ajax({
    url: jsonAuthUrl,
    dataType: 'json',
    async: false,
    data: {authStatus: 0},
    success: function(json) {
      
      if (json.flickr == false)
      {
        $("#flickrAppInput").show();
        $("#flickrStatus").addClass("authFalse");
        $("#flickrStatus").removeClass("authTrue");
      }
      else
      {
        $("#flickrStatus").removeClass("authFalse");
        $("#flickrStatus").addClass("authTrue");
      }
      
      if (json.facebook == false)
      {
        $("#facebookAppInput").show();
        $("#facebookStatus").addClass("authFalse");
        $("#facebookStatus").removeClass("authTrue");
      }
      else
      {
        $("#facebookStatus").removeClass("authFalse");
        $("#facebookStatus").addClass("authTrue");
      }
      
      if (json.tumblr == false)
      {
        $("#tumblrAppInput").show();
        $("#tumblrStatus").addClass("authFalse");
        $("#tumblrStatus").removeClass("authTrue");
      }
      else
      {
        $("#tumblrStatus").removeClass("authFalse");
        $("#tumblrStatus").addClass("authTrue");
      }

      if (json.twitter == false)
      {
        $("#twitterAppInput").show();
        $("#twitterStatus").addClass("authFalse");
        $("#twitterStatus").removeClass("authTrue");
      }
      else
      {
        $("#twitterStatus").removeClass("authFalse");
        $("#twitterStatus").addClass("authTrue");
      }
    }
  });
}

$("#flickrAppInputSubmit").click(function () {
  var apiKey = $("#flickrAPIKey").val();
  var apiSecret= $("#flickrAPISecret").val();

  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret }
  
  $.ajax({
    type: 'POST',
    url: "../auth/flickrAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Flickr auth failed - check your key/secret values");
    }
  });
});


$("#facebookAppInputSubmit").click(function () {
  var apiKey = $("#facebookAPIKey").val();
  var apiSecret= $("#facebookAPISecret").val();

  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret }
  
  $.ajax({
    type: 'POST',
    url: "../auth/facebookAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Facebook auth failed - check your key/secret values");
    }
  });
});


$("#tumblrAppInputSubmit").click(function () {
  var apiKey = $("#tumblrAPIKey").val();
  var apiSecret= $("#tumblrAPISecret").val();
  var blogURL = $("#tumblrBlogURL").val();
  
  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret, "blogURL":blogURL }
  
  $.ajax({
    type: 'POST',
    url: "../auth/tumblrAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Tumblr auth failed - check your key/secret values");
    }
  });
});


$("#twitterAppInputSubmit").click(function () {
  var apiKey = $("#twitterAPIKey").val();
  var apiSecret= $("#twitterAPISecret").val();

  submitDict = { "submitInitial":0, "apiKey":apiKey, "apiSecret":apiSecret }
  
  $.ajax({
    type: 'POST',
    url: "../auth/twitterAuth",
    dataType: 'json',
    async: false,
    data: submitDict,
    success: function(json) {
      window.location.replace(json.redirectURL);
    },
    error: function(XMLHttpRequest, textStatus, errorThrown) {
      alert("Twitter auth failed - check your key/secret values");
    }
  });
});