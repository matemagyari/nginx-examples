const http = require('http');

var request_uris = {}

function process(request) {
    let counter = request_uris[request.url] || 0
    request_uris[request.url] = counter + 1
};

let app = http.createServer((request, response) => {
    var response_body = ''
    var response_content_type = 'text/plain'

    if (request.url === '/reset') {
        request_uris = {}
        response_body = 'ok'
    }
    else if (request.url === '/state') {
        response_content_type = 'application/json'
        response_body = JSON.stringify(request_uris)
    }
    else {
        process(request)
        response_body = 'NodeJs Hello'
    }

    response.writeHead(200, {'Content-Type': response_content_type})
    response.end(response_body)
});

// Start the server on port 3000
app.listen(3000, '127.0.0.1');
console.log('Node server running on port 3000');