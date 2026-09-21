(function(root) {
  'use strict';

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function(c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function sourcesHtml(record) {
    return record.sources.map(function(name, i) {
      var label = escapeHtml(name);
      var url = (record.source_urls || [])[i];
      if (typeof url !== 'string') return label;
      try {
        var parsed = new URL(url);
        if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') return label;
      } catch (error) {
        return label;
      }
      return '<a href="' + escapeHtml(url) + '">' + label + '</a>';
    }).join(' &#183; ');
  }

  function promiseStatus(status) {
    return status === 'kept (delayed)' ? 'kept' : status;
  }

  root.DontforgetData = {
    escapeHtml: escapeHtml,
    sourcesHtml: sourcesHtml,
    promiseStatus: promiseStatus
  };
})(globalThis);
