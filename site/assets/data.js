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

  function reviewHtml(record) {
    if (!record.review) return '';
    var review = record.review;
    var fields = review.fields.map(function(field) { return field.replace(/_/g, ' '); }).join(', ');
    var sources = review.sources || [];
    return '<div class="review-note"><p><strong>Details under review:</strong> ' +
      escapeHtml(fields) + ' (' + escapeHtml(review.as_of) + ').</p><p>' +
      escapeHtml(review.note) + '</p>' + (sources.length ?
        '<div class="sources">Review evidence: ' + sourcesHtml({
          sources: sources.map(function(source) { return source.name; }),
          source_urls: sources.map(function(source) { return source.url; })
        }) + '</div>' : '') + '</div>';
  }

  root.DontforgetData = {
    escapeHtml: escapeHtml,
    sourcesHtml: sourcesHtml,
    promiseStatus: promiseStatus,
    reviewHtml: reviewHtml
  };
})(globalThis);
