/*
 * For demonstration purposes only: some Javascript functions that can
 * retrieve the value of a property of a section of a Feedmark document,
 * _after_ it has been converted to HTML and is present in a DOM.
 */

function getFeedmarkPropertyList(headingElement) {
  var sibling = headingElement;
  while (sibling) {
    if (sibling.tagName === 'UL')
      return sibling;
    sibling = sibling.nextElementSibling;
  }
  return null;
}

function getPropertyValue(propertyList, propertyName) {
  if (!propertyList) {
    return null;
  }
  for (var j = 0; j < propertyList.children.length; j++) {
    var child = propertyList.children[j];
    var propertyText = child.innerHTML;

    var colonated = propertyText.match( /^([a-zA-Z0-9 -]+)\:\s*(.*?)\s*$/ );
    if (colonated) {
      if (colonated[1] === propertyName) {
        return colonated[2];
      }
    }

    var multiple = propertyText.match( /^([a-zA-Z0-9-]+)\s*\@\s*(.*?)\s*$/ );
    if (multiple && multiple[1] === propertyName) {
      return multiple[2];
    }
  }
  return null;
}
