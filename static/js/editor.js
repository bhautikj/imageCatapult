jQuery.ajaxSettings.traditional = true;

$(function() {
  $( "#flickrSets" ).selectable({
    unselected: function(event, ui) { $("#editorSlide").data('flickrSetsDirty', true); },
    selected: function(event, ui) { $("#editorSlide").data('flickrSetsDirty', true); }                          
  });
  $( "#flickrGroups" ).selectable({
    unselected: function(event, ui) { $("#editorSlide").data('flickrGroupsDirty', true); },
    selected: function(event, ui) { $("#editorSlide").data('flickrGroupsDirty', true); }                          
  });
  

  $("#latitude").filter_input({regex:'[0-9.]'}); 
  $("#longitude").filter_input({regex:'[0-9.]'}); 

  $("#latitude").button().addClass('styledInput');
  $("#longitude").button().addClass('styledInput');
  
  
  $("#templateList").selectable();

  setInterval( "slideSwitch()", 8000 );
});

function showUploadImages()
{
  $("#uploadImages").show("drop");
  $("#imagesTab").hide("drop");
  $("#editBox").hide("drop");
  $("#authPage").hide("drop");
  $("#jobsPage").hide("drop");
}

function showAuth()
{
  $("#authPage").show("drop");
  $("#imagesTab").hide("drop");
  $("#editBox").hide("drop");
  $("#uploadImages").hide("drop");
  $("#jobsPage").hide("drop");
}

function showEditor()
{
  $("#editBox").show("drop");
  $("#imagesTab").hide("drop");
  $("#uploadImages").hide("drop");
  $("#authPage").hide("drop");
  $("#jobsPage").hide("drop");
}

function showMain()
{
  $("#imagesTab").show("drop");
  $("#editBox").hide("drop");
  $("#uploadImages").hide("drop");
  $("#authPage").hide("drop");
  $("#jobsPage").hide("drop");
}

function showJobs()
{
  $("#jobsPage").show("drop");
  $("#imagesTab").hide("drop");
  $("#editBox").hide("drop");
  $("#uploadImages").hide("drop");
  $("#authPage").hide("drop");
}

function slideSwitch() {
  var nimg =  $('#editorSlide IMG').length;
  if (nimg < 2)
    return;

  var $active = $('#editorSlide IMG.active');

  if ( $active.length == 0 ) $active = $('#editorSlide IMG:last');

  var $next =  $active.next().length ? $active.next()
  : $('#editorSlide IMG:first');

  $active.addClass('last-active');
      
  $next.css({opacity: 0.0})
  .addClass('active')
  .animate({opacity: 1.0}, 500, function() {
      $active.removeClass('active last-active');
  });
}

$("#uploadImagesButton").click(function () {
  showUploadImages();
});

$("#uploadBackButton").click(function () {
  refreshImages($( "#dbImageList" ));
  showMain();
});

$("#authBackButton").click(function () {
  refreshImages($( "#dbImageList" ));
  showMain();
});

$("#authButton").click(function () {
  showAuth();
});

$("#jobsButton").click(function () {
  setupJobsPane();
  showJobs();
});

$("#jobsBackButton").click(function () {
  showMain();
});

$( "#deleteImagesButton").click(function() {
  var selectedImages = [];
  $('#dbImageList .ui-selected').each(function(){
    var imgid =  $(this).children("img").attr("dbid");
    if (jQuery.type(imgid) != 'undefined')
    {
      selectedImages.push(imgid);
    }
  });
  
  if (selectedImages.length == 0)
    return;

  $.post('../image', 
    {deleteImagesList:JSON.stringify(selectedImages)}, 
    function(response) {}, 'json');
  
  refreshImages($( "#dbImageList" ));
});

$( "#editButton" ).click(function() {
  var selectedImages = [];
  $('#dbImageList .ui-selected').each(function(){
    var imgid =  $(this).children("img").attr("dbid");
    if (jQuery.type(imgid) != 'undefined')
    {
      selectedImages.push(imgid);
    }
  });
  
  if (selectedImages.length == 0)
    return;

  $("#editorSlide").html("");
  $("#flickrSets").html("");
  $("#flickrGroups").html("");
  $("#editTags").tagit("removeAll");
  
  var winWidth =  $(window).width();
  var winHeight = $(window).height();
  var windowAr = winWidth/winHeight;

  var authDict = {};
  
  $.ajax({
    url: "../auth",
    async: false,
    dataType: "json",
    data: {"authStatus":0},
    success: function(json) {
      for (var a in json)
      {
        authDict[a] = json[a];
      }
    }
  });
  
  if (!("flickr" in authDict))
    authDict["flickr"] = false;
  
  if (!("tumblr" in authDict))
    authDict["tumblr"] = false;
  
  if (!("facebook" in authDict))
    authDict["facebook"] = false;

  if (!("twitter" in authDict))
    authDict["twitter"] = false;  

  if (authDict["flickr"]==true)
  {
    $("#flickrOpts").show();
    // flickr is default - don't make it uncheckable for now
    $("#flickrCheck").prop('disabled', true);
  }
  else
  {
    $("#flickrOpts").hide();
  }

  // Create services button
  for (var service in authDict)
  {
    var serviceId = service + "Check";
    
    if (authDict[service] != true)
    {
      $("#" + serviceId).prop('checked', false);
      $("#" + serviceId).prop('disabled', true);
      $("#" + serviceId).hide();
    }
    else
    {
      $("#" + serviceId).show();
    }

  }
  
  
  if (authDict["flickr"] == true)
  {
    $.ajax({
      url: "../flickr",
      async: false,
      dataType: "json",
      data: {"getSets":0},
      success: function (response) {
        for (var key in response)
        {
          var li = $('<li>');
          li.attr('class','ui-widget-content')
          li.attr('value',key);
          li.text(response[key]);
          $('#flickrSets').append(li);
        }
      }
    });
    
    $.ajax({
      url: "../flickr",
      async: false,
      dataType: "json",
      data: {"getGroups":0},
      success: function (response) {
        for (var key in response)
        {
          var li = $('<li>');
          li.attr('class','ui-widget-content')
          li.attr('value',key);
          li.text(response[key]);
          $('#flickrGroups').append(li);
        }
      }
    });
  }
  
  $.post('../image', 
    {selectedList:JSON.stringify(selectedImages)}, 
    function(response) {    
      $.each(response.imageList, function (index, image) {
        var img = $('<img id="dynamic">');
        img.attr('src', image.url);
        img.attr('owidth', image.width);
        img.attr('oheight', image.height);
        var imgAr = image.width/image.height;
        
        if(imgAr>windowAr)
        {
          img.attr('height', winHeight);
        }
        else
        {
          img.attr('width', winWidth);
        }
        $('#editorSlide').append(img);
      });
      
      if (response.title != "")
      {
        $("#editTitle").text(response.title);
      }
      else
      {
        $("#editTitle").text("Title");
      }
      
      if (response.description != "")
      {
        $("#editDescription").text(response.description);
      }
      else
      {
        $("#editDescription").text("Description");
      }
      
      if (response.tags != "")
      {
        $.each(response.tags, function (index, tag) {
          $("#editTags").tagit("createTag", tag);
        });        
      }
      
      //turn these into generic function yaaa
      if (response.flickrSets != "")
        setSelectedFlickrSets(response.flickrSets);
      
      if (response.flickrGroups != "")
        setSelectedFlickrGroups(response.flickrGroups);

      if (response.jobDict != "")
      {
        for (var service in response.jobDict)
        {
          $("#" + service + "Check").prop('checked', response.jobDict[service]);
          // state has been set, now create button
          $("#" + service + "Check").button();
        }
      }
      
      $( "#otherOpts" ).buttonset();

      $("#latitude").val(response.latitude);
      $("#longitude").val(response.longitude);
      $("#geoCode").prop('checked', response.geoCode);
      
      geoCodeSetEnabled(response.geoCode);      
      
    }, 'json');
    
  
  $("#editorSlide").data('authDict', authDict);
  $("#editorSlide").data('titleDirty', false);
  $("#editorSlide").data('descriptionDirty', false);
  $("#editorSlide").data('tagsDirty', false);
  $("#editorSlide").data('flickrSetsDirty', false);
  $("#editorSlide").data('flickrGroupsDirty', false);
  $("#editorSlide").data('otherOptsDirty', false);
  $("#editorSlide").data('geoCodeDirty', false);
  
  $(".templateEdit").hide();
  $("#toggleTemplatesButton").data("shown",false);  
  $("#editBox").data("selectedImages", selectedImages);
  
  showEditor();
});

$( "#toggleTemplatesButton" ).click(function() {
  var shown = $("#toggleTemplatesButton").data("shown");
  if (shown == true)
  {
    $(".templateEdit").hide("slow");
    $("#toggleTemplatesButton").data("shown",false);
  }
  else
  {
    $(".templateEdit").show("slow");
    $("#toggleTemplatesButton").data("shown",true);
    $("#titleCheck").attr('checked', false);
    $("#descriptionCheck").attr('checked', false);
    $("#tagsCheck").attr('checked', false);
    $("#flickrSetsCheck").attr('checked', false);
    $("#flickrGroupsCheck").attr('checked', false); 
    $("#otherOptsCheck").attr('checked', false);
    $("#geoCodeCheck").attr('checked', false);
    $("#saveTemplateName").val("");
    
    updateTemplateList();
  }
});

$("#submitLoadTemplate").click(function() {
  var selectedTemplates = getSelectedTemplates();
  

  //var toLoad = $("#templateList").selectedValues();
  
  for (var i = 0; i < selectedTemplates.length; i++)
  {
    $.ajax({
      url: "../template",
      async: false,
      dataType: "json",
      data: {getTemplate:selectedTemplates[i]},
      success: function( data ) { 
        var title = data.title;
        if (title != undefined)
        {
          $("#editTitle").text(title);
          $("#editorSlide").data('titleDirty', true);
        }
        
        var description = data.description;
        if (description != undefined)
        {
          $("#editDescription").text(description);
          $("#editorSlide").data('descriptionDirty', true);
        }
        
        var tags = data.tags;
        if (tags != undefined)
        {
          var tagSet = JSON.parse(tags);
          for (var i = 0; i < tagSet.length; i++) 
          {
            $("#editTags").tagit("createTag", tagSet[i]);
            $("#editorSlide").data('tagsDirty', true);
          }
        }
        
        var flickrSets = data.flickrSets;
        if (flickrSets != undefined)
        {
          var flickrSetsArray = JSON.parse(flickrSets);
          setSelectedFlickrSets(flickrSetsArray);
          $("#editorSlide").data('flickrSetsDirty', true);
        }
        
        var flickrGroups = data.flickrGroups;
        if (flickrGroups != undefined)
        {
          var flickrGroupsArray = JSON.parse(flickrGroups);
          setSelectedFlickrGroups(flickrGroupsArray);
          $("#editorSlide").data('flickrGroupsDirty', true);
        }
        
        var geoCode = data.geoCode;
        if (geoCode != undefined)
        {
          $("#editorSlide").data('geoCodeDirty', true);
          $("#geoCode").prop('checked', geoCode);
          geoCodeSetEnabled(geoCode);      
        }
        
        var latitude = data.latitude;
        if (latitude != undefined)
        {
          $("#latitude").val(latitude);
        }
        
        var longitude = data.longitude;
        if (longitude != undefined)
        {
          $("#longitude").val(longitude);
        }
      }
      
    });
  
  }
  
});

$("#submitSaveTemplate").click(function() {
  var templateDict = {};
  var titleChecked = $("#titleCheck").is(':checked');
  var descriptionCheck = $("#descriptionCheck").is(':checked');
  var tagsCheck = $("#tagsCheck").is(':checked');
  var flickrSetsCheck = $("#flickrSetsCheck").is(':checked');
  var flickrGroupsCheck = $("#flickrGroupsCheck").is(':checked');
  var geoCodeCheck =$("#geoCodeCheck").is(':checked');
  var otherOptsCheck = $("#otherOptsCheck").is(':checked');
  
  var templateName = $("#saveTemplateName").val();
  if (templateName == "")
    return;
  
  templateDict["saveTemplate"] = templateName;
  
  //alert(titleChecked + "," + descriptionCheck + "," + tagsCheck);
  
  if (titleChecked)
  {
    var title = $("#editTitle").html();
    templateDict["title"] = title;
  }
  
  if (descriptionCheck)
  {
    var description = $("#editDescription").html();
    templateDict["description"] = description;
  }
  
  if (tagsCheck)
  {
    var tags = $("#editTags").tagit("assignedTags");
    templateDict["tags"] = JSON.stringify(tags);
  }
  
  if (flickrSetsCheck)
  {
    var flickrSets = getSelectedFlickrSets();
    templateDict["flickrSets"] = JSON.stringify(flickrSets);
  }
  
  if (flickrGroupsCheck)
  {
    var flickrGroups = getSelectedFlickrGroups();
    templateDict["flickrGroups"] = JSON.stringify(flickrGroups);    
  }
  
  if (geoCodeCheck)
  {
    templateDict["geoCode"] = $("#geoCode").is(":checked");
    templateDict["latitude"] = $("#latitude").val();
    templateDict["longitude"] = $("#longitude").val();
  }

  $.ajax({
    url: "../template",
    async: true,
    dataType: "json",
    data: templateDict,
    success: function( data ) { updateTemplateList(); }
  });
  
});

function updateTemplateList()
{
  $.ajax({
    url: "../template",
    async: false,
    dataType: "json",
    data: {"templateList":0},
    success: function( response ) {
      $("#templateList").html("");
      for (var key in response)
      {
        var li = $('<li>');
        li.attr('class','ui-widget-content')
        li.attr('value',key);
        li.text(response[key]);
        $('#templateList').append(li);
      }
    }
  });
}

function setSelectedFlickrSets(flickrSets)
{
  for (var i = 0; i < flickrSets.length; i++) 
  {
    var element = $("#flickrSets [value='" + flickrSets[i] + "']")
    element.addClass("ui-selected");     
  }
  //$("#flickrSets").data("selectable")._mouseStop(null);
}

function setSelectedFlickrGroups(flickrGroups)
{
  for (var i = 0; i < flickrGroups.length; i++) 
  {
    var element = $("#flickrGroups [value='" + flickrGroups[i] + "']")
    element.addClass("ui-selected");     
  }
  //$("#flickrGroups").data("selectable")._mouseStop(null);
}

function getSelectedFlickrSets()
{
  var flickrSets = [];
  $("#flickrSets .ui-selected").each(function(){
    var setid =  $(this).attr("value");
    flickrSets.push(setid);
  });
  return flickrSets;
}

function getSelectedFlickrGroups()
{
  var flickrGroups = [];
  $("#flickrGroups .ui-selected").each(function(){
    var setid =  $(this).attr("value");
    flickrGroups.push(setid);
  });
  return flickrGroups;
}

function getSelectedTemplates()
{
  var selectedTemplates = [];
  $("#templateList .ui-selected").each(function(){
    var templateId =  $(this).attr("value");
    selectedTemplates.push(templateId);
  }); 
  return selectedTemplates;
}

$( "#applyEditsButton" ).click(function() {
  
  //   teardown
  var title = $("#editTitle").html();
  var description = $("#editDescription").html();
  var selectedImages = $("#editBox").data("selectedImages");
  var tags = $("#editTags").tagit("assignedTags");
  
  var titleDirty = $("#editorSlide").data('titleDirty');
  var descriptionDirty = $("#editorSlide").data('descriptionDirty');
  var tagsDirty = $("#editorSlide").data('tagsDirty');
  var flickrSetsDirty = $("#editorSlide").data('flickrSetsDirty');
  var flickrGroupsDirty = $("#editorSlide").data('flickrGroupsDirty');
  var otherOptsDirty = $("#editorSlide").data('otherOptsDirty');
  var geoCodeDirty = $("#editorSlide").data('geoCodeDirty');
  var authDict = $("#editorSlide").data("authDict");
  
  //alert(titleDirty + "," + descriptionDirty + "," + tagsDirty);
  var submitDict = {};
  submitDict["submitList"] = JSON.stringify(selectedImages);
  
  if (titleDirty)
    submitDict["title"] = JSON.stringify(title);
  
  if (descriptionDirty)
    submitDict["description"] = JSON.stringify(description);
  
  if(tagsDirty)
    submitDict["tags"] = JSON.stringify(tags);

  if (authDict["flickr"] == true)
  {
    var flickrSets = getSelectedFlickrSets();
    var flickrGroups = getSelectedFlickrGroups();

    if (flickrSetsDirty)
      submitDict["flickrSets"] = JSON.stringify(flickrSets);
    
    if (flickrGroupsDirty)
      submitDict["flickrGroups"] = JSON.stringify(flickrGroups);
  }
  
  if (geoCodeDirty)
  {
    submitDict["geoCode"] = $("#geoCode").is(":checked");
    submitDict["latitude"] = $("#latitude").val();
    submitDict["longitude"] = $("#longitude").val();
  }
  
  //TODO: just dump the otherOpts for now, need proper notification
  //if its dirty and make them templatable
  
  var jobDict = {}  
  jobDict["flickr"] = $("#flickrCheck").is(':checked');
  jobDict["tumblr"] = $("#tumblrCheck").is(':checked');
  jobDict["twitter"] = $("#twitterCheck").is(':checked');
  jobDict["facebook"] = $("#facebookCheck").is(':checked');
  
  var jobDictString = JSON.stringify(jobDict);
  submitDict["jobDict"] = jobDictString;
  
  $.post('../image', 
    submitDict, 
    function(response) {    
      //no-op, probably
    }, 'json');
  
  $("#editorSlide").html("");
  $("#editBox").data("selectedImages", null);
  
  showMain();
});

$( "#cancelEditsButton" ).click(function() {
  //   teardown
  $("#editorSlide").html("");
  $("#editBox").data("selectedImages", null);
  showMain();
});



$("#editTitle").editInPlace({
  callback: function(unused, enteredText) { $("#editorSlide").data('titleDirty', true); return enteredText; },
  show_buttons: true
});

$("#editDescription").editInPlace({
  callback: function(unused, enteredText) { $("#editorSlide").data('descriptionDirty', true); return enteredText; },
  field_type: "textarea",
  show_buttons: true
});


function geoCodeSetEnabled(enableGeoCode)
{
  if (enableGeoCode)
  {
    $("#longitude").prop('disabled', false);
    $("#latitude").prop('disabled', false);
  }
  else
  {
    $("#longitude").prop('disabled', true);
    $("#latitude").prop('disabled', true);
  }    
}

$("#geoCode").click(function() {
  $("#editorSlide").data('geoCodeDirty', true);
  if($("#geoCode").is(':checked'))
    geoCodeSetEnabled(true);
  else
    geoCodeSetEnabled(false);
});


$("#editTags").tagit({
autocomplete: { source: function( request, response ) {
  $.ajax({
    url: "../tags",
    dataType: "json",
    data: {
      searchTags: request.term
    },
    success: function( data ) {
    response( $.map( data.results, function( item ) {
      return {
        label: item,
        value: item
      }
      }));
    }
  });
  },
    minLength: 2 
  },
placeholderText: "add tags...",
afterTagAdded: function(event, ui) {
    //console.log(ui.tag);
  $("#editorSlide").data('tagsDirty', true);
},
afterTagRemoved: function(event, ui) {
    //console.log(ui.tag);
  $("#editorSlide").data('tagsDirty', true);
}

});