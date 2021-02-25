function ajaxCall(){this.send=function(data,url,method,success,type){type=type||'json';var successRes=function(data){success(data);}
var errorRes=function(e){}
jQuery.ajax({url:url,type:method,data:data,success:successRes,error:errorRes,dataType:type,timeout:60000});}}
function locationInfo(){var rootUrl="//geodata.solutions/api/api.php";var username='demo';var ordering='name';var addParams='';if(jQuery("#gds_appid").length>0){addParams+='&appid='+jQuery("#gds_appid").val();}
if(jQuery("#gds_hash").length>0){addParams+='&hash='+jQuery("#gds_hash").val();}
var call=new ajaxCall();this.confCity=function(id){var url=rootUrl+'?type=confCity&countryId='+jQuery('#countryId option:selected').attr('countryid')+'&stateId='+id;var method="post";var data={};call.send(data,url,method,function(data){if(data){}
else{}});};this.getStates=function(id){jQuery(".states option:gt(0)").remove();jQuery(".cities option:gt(0)").remove();var stateClasses=jQuery('#stateId').attr('class');var cC=stateClasses.split(" ");cC.shift();var addClasses='';if(cC.length>0)
{acC=cC.join();addClasses='&addClasses='+encodeURIComponent(acC);}
var url=rootUrl+'?type=getStates&countryId='+id+addParams+addClasses;var method="post";var data={};jQuery('.states').find("option:eq(0)").html("Please wait..");call.send(data,url,method,function(data){jQuery('.states').find("option:eq(0)").html("Select State");if(data.tp==1){if(data.hits>1000)
{console.log('Daily geodata.solutions request limit exceeded: '+data.hits+' of 1000.');}
else
{console.log('Daily geodata.solutions request count:'+data.hits+' of 1000')}
jQuery.each(data['result'],function(key,val){var option=jQuery('<option />');option.attr('value',val).text(val);option.attr('stateid',key);jQuery('.states').append(option);});jQuery(".states").prop("disabled",false);}
else{alert(data.msg);}});};this.getCountries=function(){var countryClasses=jQuery('#countryId').attr('class');var cC=countryClasses.split(" ");cC.shift();var addClasses='';if(cC.length>0)
{acC=cC.join();addClasses='&addClasses='+encodeURIComponent(acC);}
var presel=false;var iip='N';jQuery.each(cC,function(index,value){if(value.match("^presel-")){presel=value.substring(7);console.log('1 presel is set as '+presel);}
if(value.match("^presel-byi"))
{var iip='Y';}});var url=rootUrl+'?type=getCountries'+addParams+addClasses;var method="post";var data={};jQuery('.countries').find("option:eq(0)").html("Please wait..");call.send(data,url,method,function(data){jQuery('.countries').find("option:eq(0)").html("Select Country");if(data.tp==1){if(data.hits>1000)
{console.log('Daily geodata.solutions request limit exceeded: '+data.hits+' of 1000.');}
else
{console.log('Daily geodata.solutions request count:'+data.hits+' of 1000')}
if(presel=='byip')
{presel=data['presel'];console.log('2 presel is set as '+presel);}
if(jQuery.inArray("group-continents",cC)>-1)
{var $select=jQuery('.countries');jQuery.each(data['result'],function(i,optgroups){var $optgroup=jQuery("<optgroup>",{label:i});if(optgroups.length>0)
{$optgroup.appendTo($select);}
jQuery.each(optgroups,function(groupName,options){var coption=jQuery('<option />');coption.attr('value',options.name).text(options.name);coption.attr('countryid',options.id);if(presel){if(presel.toUpperCase()==options.id){coption.attr('selected','selected');}}
coption.appendTo($optgroup);});});}
else
{jQuery.each(data['result'],function(key,val){var option=jQuery('<option />');option.attr('value',val).text(val);option.attr('countryid',key);if(presel)
{if(presel.toUpperCase()==key)
{option.attr('selected','selected');}}
jQuery('.countries').append(option);});}
if(presel)
{jQuery('.countries').trigger('change');}
jQuery(".countries").prop("disabled",false);}
else{alert(data.msg);}});};}
jQuery(function(){var loc=new locationInfo();loc.getCountries();jQuery(".countries").on("change",function(ev){var countryId=jQuery("option:selected",this).attr('countryid');if(countryId!=''){loc.getStates(countryId);}
else{jQuery(".states option:gt(0)").remove();}});jQuery(".states").on("change",function(ev){var stateId=jQuery("option:selected",this).val();if(stateId!=''){loc.confCity(stateId);}});});