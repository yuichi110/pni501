<?php

declare(strict_types=1);

use App\Http\Controllers\OrderController;
use Illuminate\Support\Facades\Route;

Route::middleware('auth:sanctum')->group(function (): void {
    Route::get('/orders', [OrderController::class, 'listRecent']);
    Route::post('/orders', [OrderController::class, 'store']);
});
