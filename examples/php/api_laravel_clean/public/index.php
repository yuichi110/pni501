<?php

declare(strict_types=1);

namespace App\Http;

/**
 * Resolve HTTP status and JSON body for liveness/readiness probes.
 *
 * @param string $uriPath Normalized request URI path.
 * @return array<string, int|string>
 */
function buildHealthResponse(string $uriPath): array
{
    if ($uriPath === '/up' || $uriPath === '/healthz' || $uriPath === '/') {
        return [
            'http_code' => 200,
            'service' => 'order-fulfillment-api',
            'status' => 'ok',
        ];
    }

    return [
        'http_code' => 404,
        'service' => 'order-fulfillment-api',
        'status' => 'not_found',
    ];
}

if (PHP_SAPI !== 'cli') {
    $rawUri = filter_input(INPUT_SERVER, 'REQUEST_URI', FILTER_SANITIZE_URL);
    $path = is_string($rawUri) && $rawUri !== ''
        ? (string) parse_url($rawUri, PHP_URL_PATH)
        : '/';
    $payload = buildHealthResponse($path);
    http_response_code((int) $payload['http_code']);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_THROW_ON_ERROR);
}
