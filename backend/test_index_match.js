function testIndexMatch() {
  // Simulate the index we'd build from root folders
  var mockIndex = {
    'sreyka bora': 'id1',
    'chea kimlang': 'id2',
    'yort rayun - d2 visa': 'id3',    // folder has extra suffix
    'bora / sreyka': 'id4',
    'kimlang chea': 'id5',             // last-first order
    'rathana an': 'id6'
  };

  function findFolderId(name) {
    var label = name.replace(/[\\/:*?"<>|]/g,'').trim().toLowerCase();
    
    // 1) exact match
    if (mockIndex[label]) return mockIndex[label];
    
    // 2) try tokens (first-name / last-name permutations)
    var tokens = label.split(/[\s,;]+/).filter(Boolean);
    if (tokens.length >= 2) {
      // try "last first" order (reversal)
      var reversed = tokens.slice(1).join(' ') + ' ' + tokens[0];
      if (mockIndex[reversed]) return mockIndex[reversed];
      
      // try each token as substring (folder might be "FIRST LAST - PROGRAM")
      for (var k in mockIndex) {
        // all tokens present in the key (in any order)
        var allMatch = tokens.every(function(t){ return k.indexOf(t) >= 0; });
        if (allMatch) return mockIndex[k];
      }
    }
    
    // 3) single token: find first key containing it
    if (tokens.length === 1) {
      for (var k in mockIndex) {
        if (k.indexOf(tokens[0]) >= 0) return mockIndex[k];
      }
    }
    
    return null;
  }

  var tests = [
    { name: 'BORA SREYKA', expect: 'id1' },
    { name: 'SREYKA BORA', expect: 'id1' },           // reversed
    { name: 'CHEA KIMLANG', expect: 'id2' },
    { name: 'YORT RAYUN', expect: 'id3' },             // folder is "yort rayun - d2 visa"
    { name: 'BORA SREYKA', expect: 'id1' },
    { name: 'KIMLANG CHEA', expect: 'id5' },           // last-first folder
    { name: 'AN RATHANA', expect: 'id6' },
    { name: 'UNKNOWN STUDENT', expect: null }
  ];
  
  var pass = 0, fail = 0;
  tests.forEach(function(t){
    var got = findFolderId(t.name);
    if (got === t.expect) pass++;
    else { fail++; console.log('FAIL: ' + t.name + ' expected ' + t.expect + ' got ' + got); }
  });
  console.log(pass + '/' + (pass+fail) + ' passed');
}

testIndexMatch();