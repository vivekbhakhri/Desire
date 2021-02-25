/**********************************

Orinal code from this article:
http://www.barneyparker.com/world-simplest-html5-wysisyg-inline-editor/

**********************************/

$(function() {
  $('#editControls a').click(function(e) {
    switch($(this).data('role')) {
      case 'h1':
      case 'h2':
      case 'p':
        document.execCommand('formatBlock', false, $(this).data('role'));
        break;
      default:
        document.execCommand($(this).data('role'), false, null);
        break;
    }
    
  });
});