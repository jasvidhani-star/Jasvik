<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Trending Songs Uploader</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        :root {
            --bg: #0a0a0f;
            --bg2: #111118;
            --card: rgba(22, 22, 32, 0.85);
            --card-hover: rgba(30, 30, 45, 0.95);
            --border: rgba(255, 255, 255, 0.06);
            --border-accent: rgba(255, 107, 53, 0.3);
            --fg: #f0ece6;
            --fg-muted: #8a8694;
            --accent: #ff6b35;
            --accent2: #ff3d00;
            --accent-glow: rgba(255, 107, 53, 0.25);
            --success: #00e676;
            --warning: #ffab00;
            --error: #ff1744;
            --info: #00b0ff;
            --glass: rgba(255, 255, 255, 0.03);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg);
            color: var(--fg);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* === ANIMATED BACKGROUND === */
        .bg-scene {
            position: fixed;
            inset: 0;
            z-index: 0;
            overflow: hidden;
            pointer-events: none;
        }

        .bg-scene .orb {
            position: absolute;
            border-radius: 50%;
            filter: blur(120px);
            animation: orbFloat 12s ease-in-out infinite;
        }

        .bg-scene .orb:nth-child(1) {
            width: 500px; height: 500px;
            background: radial-gradient(circle, rgba(255,107,53,0.15), transparent 70%);
            top: -10%; left: -5%;
            animation-duration: 15s;
        }

        .bg-scene .orb:nth-child(2) {
            width: 400px; height: 400px;
            background: radial-gradient(circle, rgba(255,61,0,0.1), transparent 70%);
            bottom: -15%; right: -5%;
            animation-duration: 18s;
            animation-delay: -5s;
        }

        .bg-scene .orb:nth-child(3) {
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(255,171,0,0.08), transparent 70%);
            top: 40%; left: 50%;
            animation-duration: 20s;
            animation-delay: -8s;
        }

        .bg-grid {
            position: fixed;
            inset: 0;
            z-index: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
            background-size: 60px 60px;
            pointer-events: none;
        }

        @keyframes orbFloat {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(30px, -40px) scale(1.1); }
            66% { transform: translate(-20px, 20px) scale(0.95); }
        }

        /* === LAYOUT === */
        .app-container {
            position: relative;
            z-index: 1;
            display: flex;
            min-height: 100vh;
        }

        /* === SIDEBAR === */
        .sidebar {
            width: 260px;
            background: var(--bg2);
            border-right: 1px solid var(--border);
            padding: 24px 0;
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0;
            left: 0;
            height: 100vh;
            z-index: 10;
            transition: transform 0.3s ease;
        }

        .sidebar-brand {
            padding: 0 24px 28px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 16px;
        }

        .sidebar-brand h2 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 18px;
            font-weight: 700;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .sidebar-brand h2 i {
            font-size: 22px;
        }

        .sidebar-brand span {
            font-size: 11px;
            color: var(--fg-muted);
            display: block;
            margin-top: 4px;
            font-weight: 400;
        }

        .nav-section {
            padding: 0 12px;
            flex: 1;
        }

        .nav-label {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--fg-muted);
            padding: 12px 12px 8px;
            font-weight: 600;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 11px 16px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 14px;
            font-weight: 500;
            color: var(--fg-muted);
            margin-bottom: 2px;
            position: relative;
        }

        .nav-item:hover {
            background: var(--glass);
            color: var(--fg);
        }

        .nav-item.active {
            background: var(--accent-glow);
            color: var(--accent);
            border: 1px solid var(--border-accent);
        }

        .nav-item i {
            width: 20px;
            text-align: center;
            font-size: 15px;
        }

        .nav-item .badge {
            margin-left: auto;
            background: var(--accent);
            color: #fff;
            font-size: 10px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 20px;
        }

        .sidebar-footer {
            padding: 16px 20px;
            border-top: 1px solid var(--border);
        }

        .sidebar-footer .user-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .sidebar-footer .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
            color: #fff;
        }

        .sidebar-footer .user-name {
            font-size: 13px;
            font-weight: 600;
        }

        .sidebar-footer .user-role {
            font-size: 11px;
            color: var(--fg-muted);
        }

        /* === MAIN CONTENT === */
        .main-content {
            margin-left: 260px;
            flex: 1;
            padding: 28px 32px;
            max-width: calc(100% - 260px);
        }

        /* === TOP BAR === */
        .top-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
        }

        .top-bar h1 {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 28px;
            font-weight: 700;
        }

        .top-bar h1 span {
            color: var(--accent);
        }

        .top-actions {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        /* === BUTTONS === */
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: 10px;
            border: none;
            font-family: 'Outfit', sans-serif;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            color: #fff;
            box-shadow: 0 4px 20px var(--accent-glow);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(255,107,53,0.4);
        }

        .btn-secondary {
            background: var(--card);
            color: var(--fg);
            border: 1px solid var(--border);
        }

        .btn-secondary:hover {
            border-color: var(--border-accent);
            background: var(--card-hover);
        }

        .btn-ghost {
            background: transparent;
            color: var(--fg-muted);
            padding: 8px 12px;
        }

        .btn-ghost:hover {
            color: var(--fg);
            background: var(--glass);
        }

        .btn-sm {
            padding: 7px 14px;
            font-size: 12px;
        }

        .btn-icon {
            width: 38px;
            height: 38px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            border: 1px solid var(--border);
            background: var(--card);
            color: var(--fg-muted);
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-icon:hover {
            border-color: var(--border-accent);
            color: var(--accent);
        }

        /* === STATS ROW === */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
        }

        .stat-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .stat-card:hover {
            border-color: var(--border-accent);
            transform: translateY(-3px);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
        }

        .stat-card:nth-child(1)::before { background: linear-gradient(90deg, var(--accent), transparent); }
        .stat-card:nth-child(2)::before { background: linear-gradient(90deg, var(--success), transparent); }
        .stat-card:nth-child(3)::before { background: linear-gradient(90deg, var(--warning), transparent); }
        .stat-card:nth-child(4)::before { background: linear-gradient(90deg, var(--info), transparent); }

        .stat-icon {
            width: 42px;
            height: 42px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            margin-bottom: 14px;
        }

        .stat-card:nth-child(1) .stat-icon { background: rgba(255,107,53,0.15); color: var(--accent); }
        .stat-card:nth-child(2) .stat-icon { background: rgba(0,230,118,0.12); color: var(--success); }
        .stat-card:nth-child(3) .stat-icon { background: rgba(255,171,0,0.12); color: var(--warning); }
        .stat-card:nth-child(4) .stat-icon { background: rgba(0,176,255,0.12); color: var(--info); }

        .stat-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 4px;
        }

        .stat-label {
            font-size: 12px;
            color: var(--fg-muted);
            font-weight: 500;
        }

        /* === SECTION === */
        .section {
            display: none;
        }

        .section.active {
            display: block;
            animation: fadeSlideIn 0.4s ease;
        }

        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(16px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }

        .section-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 20px;
            font-weight: 700;
        }

        /* === SEARCH BAR === */
        .search-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 24px;
        }

        .search-input-wrap {
            flex: 1;
            position: relative;
        }

        .search-input-wrap i {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--fg-muted);
            font-size: 14px;
        }

        .search-input-wrap input {
            width: 100%;
            padding: 12px 16px 12px 42px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--fg);
            font-family: 'Outfit', sans-serif;
            font-size: 14px;
            outline: none;
            transition: all 0.25s ease;
        }

        .search-input-wrap input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }

        .search-input-wrap input::placeholder {
            color: var(--fg-muted);
        }

        /* === TRENDING SONGS GRID === */
        .songs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
        }

        .song-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
            transition: all 0.3s ease;
            position: relative;
        }

        .song-card:hover {
            border-color: var(--border-accent);
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.3);
        }

        .song-thumb {
            width: 100%;
            height: 170px;
            object-fit: cover;
            display: block;
            position: relative;
        }

        .song-thumb-wrap {
            position: relative;
            overflow: hidden;
        }

        .song-thumb-wrap::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 60px;
            background: linear-gradient(transparent, rgba(10,10,15,0.8));
        }

        .song-rank {
            position: absolute;
            top: 10px;
            left: 10px;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(10px);
            color: var(--accent);
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 14px;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            z-index: 2;
        }

        .song-duration {
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.8);
            color: #fff;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 6px;
            z-index: 2;
        }

        .song-info {
            padding: 16px;
        }

        .song-title {
            font-weight: 700;
            font-size: 15px;
            margin-bottom: 6px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .song-artist {
            font-size: 13px;
            color: var(--fg-muted);
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .song-meta {
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 11px;
            color: var(--fg-muted);
            margin-bottom: 14px;
        }

        .song-meta span {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .song-actions {
            display: flex;
            gap: 8px;
        }

        .song-actions .btn {
            flex: 1;
            justify-content: center;
            font-size: 12px;
            padding: 8px 12px;
        }

        .btn-add {
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            color: #fff;
            border: none;
        }

        .btn-add:hover {
            opacity: 0.9;
        }

        .btn-added {
            background: rgba(0,230,118,0.15);
            color: var(--success);
            border: 1px solid rgba(0,230,118,0.3);
        }

        /* === UPLOAD QUEUE TABLE === */
        .queue-container {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
        }

        .queue-header-bar {
            padding: 18px 20px;
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .queue-header-bar h3 {
            font-weight: 700;
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .queue-count {
            background: var(--accent);
            color: #fff;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 20px;
        }

        .queue-list {
            list-style: none;
        }

        .queue-item {
            display: grid;
            grid-template-columns: 40px 60px 1fr 120px 130px 100px 80px;
            align-items: center;
            gap: 14px;
            padding: 14px 20px;
            border-bottom: 1px solid var(--border);
            transition: background 0.2s ease;
        }

        .queue-item:hover {
            background: var(--glass);
        }

        .queue-item:last-child {
            border-bottom: none;
        }

        .queue-num {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 14px;
            color: var(--fg-muted);
        }

        .queue-thumb {
            width: 56px;
            height: 38px;
            border-radius: 6px;
            object-fit: cover;
        }

        .queue-song-info .q-title {
            font-weight: 600;
            font-size: 13px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 280px;
        }

        .queue-song-info .q-artist {
            font-size: 11px;
            color: var(--fg-muted);
        }

        /* Progress bar */
        .progress-wrap {
            width: 100%;
        }

        .progress-label {
            font-size: 11px;
            color: var(--fg-muted);
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
        }

        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.06);
            border-radius: 10px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--accent), var(--accent2));
            transition: width 0.4s ease;
            position: relative;
        }

        .progress-fill.complete {
            background: linear-gradient(90deg, var(--success), #00c853);
        }

        .progress-fill.error {
            background: var(--error);
        }

        /* Status badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            font-size: 11px;
            font-weight: 600;
            padding: 5px 12px;
            border-radius: 20px;
        }

        .status-pending {
            background: rgba(255,255,255,0.06);
            color: var(--fg-muted);
        }

        .status-uploading {
            background: rgba(255,107,53,0.15);
            color: var(--accent);
            animation: statusPulse 1.5s ease-in-out infinite;
        }

        .status-complete {
            background: rgba(0,230,118,0.12);
            color: var(--success);
        }

        .status-error {
            background: rgba(255,23,68,0.12);
            color: var(--error);
        }

        @keyframes statusPulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        .queue-item-actions {
            display: flex;
            gap: 6px;
        }

        /* === API CONFIG === */
        .config-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .config-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 24px;
        }

        .config-card.full-width {
            grid-column: 1 / -1;
        }

        .config-card h3 {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .config-card h3 i {
            color: var(--accent);
        }

        .config-card p {
            font-size: 12px;
            color: var(--fg-muted);
            margin-bottom: 18px;
        }

        .form-group {
            margin-bottom: 16px;
        }

        .form-group:last-child {
            margin-bottom: 0;
        }

        .form-label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--fg-muted);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-input {
            width: 100%;
            padding: 11px 14px;
            background: rgba(0,0,0,0.3);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--fg);
            font-family: 'Space Grotesk', monospace;
            font-size: 13px;
            outline: none;
            transition: all 0.25s ease;
        }

        .form-input:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }

        .form-input::placeholder {
            color: rgba(138,134,148,0.5);
        }

        textarea.form-input {
            resize: vertical;
            min-height: 100px;
        }

        .form-hint {
            font-size: 11px;
            color: var(--fg-muted);
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .form-hint i {
            color: var(--warning);
            font-size: 10px;
        }

        /* === GITHUB REFERENCE === */
        .github-ref {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 24px;
            margin-top: 20px;
        }

        .github-ref h3 {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .github-ref h3 i {
            color: #fff;
        }

        .code-block {
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            font-family: 'Space Grotesk', monospace;
            font-size: 12px;
            line-height: 1.8;
            color: #c9d1d9;
            overflow-x: auto;
            position: relative;
            margin-top: 12px;
        }

        .code-block .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(255,255,255,0.08);
            border: 1px solid var(--border);
            color: var(--fg-muted);
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Outfit', sans-serif;
        }

        .code-block .copy-btn:hover {
            background: var(--accent);
            color: #fff;
            border-color: var(--accent);
        }

        .code-kw { color: var(--accent); }
        .code-str { color: var(--success); }
        .code-cm { color: var(--fg-muted); font-style: italic; }
        .code-fn { color: #79c0ff; }
        .code-num { color: var(--warning); }

        /* === TOAST === */
        .toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .toast {
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 13px;
            font-weight: 500;
            box-shadow: 0 10px 40px rgba(0,0,0,0.4);
            animation: toastIn 0.35s ease;
            min-width: 280px;
            backdrop-filter: blur(20px);
        }

        .toast.success { border-left: 3px solid var(--success); }
        .toast.error { border-left: 3px solid var(--error); }
        .toast.info { border-left: 3px solid var(--info); }
        .toast.warning { border-left: 3px solid var(--warning); }

        .toast.hiding {
            animation: toastOut 0.3s ease forwards;
        }

        @keyframes toastIn {
            from { opacity: 0; transform: translateX(40px); }
            to { opacity: 1; transform: translateX(0); }
        }

        @keyframes toastOut {
            to { opacity: 0; transform: translateX(40px); }
        }

        /* === MODAL === */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(6px);
            z-index: 100;
            display: none;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.25s ease;
        }

        .modal-overlay.show {
            display: flex;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .modal {
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 16px;
            width: 90%;
            max-width: 520px;
            padding: 28px;
            animation: modalSlide 0.3s ease;
        }

        @keyframes modalSlide {
            from { opacity: 0; transform: translateY(20px) scale(0.97); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        .modal h3 {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .modal p {
            font-size: 13px;
            color: var(--fg-muted);
            margin-bottom: 20px;
        }

        .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 24px;
        }

        /* === EMPTY STATE === */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--fg-muted);
        }

        .empty-state i {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.3;
        }

        .empty-state h3 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--fg);
        }

        .empty-state p {
            font-size: 13px;
        }

        /* === UPLOAD ANIMATION === */
        .upload-progress-overlay {
            position: fixed;
            inset: 0;
            background: rgba(10,10,15,0.92);
            backdrop-filter: blur(12px);
            z-index: 200;
            display: none;
            align-items: center;
            justify-content: center;
        }

        .upload-progress-overlay.show {
            display: flex;
        }

        .upload-progress-box {
            text-align: center;
            width: 400px;
        }

        .upload-circle {
            width: 140px;
            height: 140px;
            margin: 0 auto 24px;
            position: relative;
        }

        .upload-circle svg {
            width: 100%;
            height: 100%;
            transform: rotate(-90deg);
        }

        .upload-circle .track {
            fill: none;
            stroke: rgba(255,255,255,0.06);
            stroke-width: 6;
        }

        .upload-circle .fill-ring {
            fill: none;
            stroke: url(#grad);
            stroke-width: 6;
            stroke-linecap: round;
            stroke-dasharray: 408;
            stroke-dashoffset: 408;
            transition: stroke-dashoffset 0.5s ease;
        }

        .upload-circle .center-text {
            position: absolute;
            inset: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .upload-circle .percent {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 32px;
            font-weight: 700;
        }

        .upload-circle .sub-text {
            font-size: 11px;
            color: var(--fg-muted);
        }

        .upload-current-song {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 6px;
        }

        .upload-counter {
            font-size: 13px;
            color: var(--fg-muted);
            margin-bottom: 20px;
        }

        /* === MOBILE === */
        .mobile-toggle {
            display: none;
            position: fixed;
            top: 16px;
            left: 16px;
            z-index: 20;
            width: 40px;
            height: 40px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--fg);
            font-size: 18px;
            cursor: pointer;
            align-items: center;
            justify-content: center;
        }

        @media (max-width: 1024px) {
            .stats-row { grid-template-columns: repeat(2, 1fr); }
            .config-grid { grid-template-columns: 1fr; }
            .queue-item { grid-template-columns: 30px 50px 1fr 80px 80px; }
            .queue-item:nth-child(n) .queue-item-actions,
            .queue-item:nth-child(n) .queue-meta-col { display: none; }
        }

        @media (max-width: 768px) {
            .mobile-toggle { display: flex; }
            .sidebar { transform: translateX(-100%); }
            .sidebar.open { transform: translateX(0); }
            .main-content { margin-left: 0; padding: 20px 16px; padding-top: 60px; max-width: 100%; }
            .stats-row { grid-template-columns: 1fr 1fr; gap: 10px; }
            .songs-grid { grid-template-columns: 1fr; }
            .top-bar h1 { font-size: 20px; }
            .search-bar { flex-direction: column; }
        }

        /* === SPINNER === */
        .spinner {
            width: 16px;
            height: 16px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            display: inline-block;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

        /* Floating music notes animation */
        .floating-notes {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
        }

        .note {
            position: absolute;
            font-size: 20px;
            color: var(--accent);
            opacity: 0;
            animation: noteFloat 8s ease-in-out infinite;
        }

        @keyframes noteFloat {
            0% { opacity: 0; transform: translateY(100vh) rotate(0deg); }
            10% { opacity: 0.15; }
            90% { opacity: 0.15; }
            100% { opacity: 0; transform: translateY(-10vh) rotate(360deg); }
        }
    </style>
</head>
<body>

<!-- Background -->
<div class="bg-scene">
    <div class="orb"></div>
    <div class="orb"></div>
    <div class="orb"></div>
</div>
<div class="bg-grid"></div>
<div class="floating-notes" id="floatingNotes"></div>

<!-- Toast Container -->
<div class="toast-container" id="toastContainer"></div>

<!-- Mobile Toggle -->
<button class="mobile-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">
    <i class="fas fa-bars"></i>
</button>

<!-- Upload Progress Overlay -->
<div class="upload-progress-overlay" id="uploadOverlay">
    <div class="upload-progress-box">
        <div class="upload-circle">
            <svg viewBox="0 0 140 140">
                <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" style="stop-color:#ff6b35"/>
                        <stop offset="100%" style="stop-color:#ff3d00"/>
                    </linearGradient>
                </defs>
                <circle class="track" cx="70" cy="70" r="65"/>
                <circle class="fill-ring" id="uploadRing" cx="70" cy="70" r="65"/>
            </svg>
            <div class="center-text">
                <span class="percent" id="uploadPercent">0%</span>
                <span class="sub-text">Uploading</span>
            </div>
        </div>
        <div class="upload-current-song" id="uploadSongName">---</div>
        <div class="upload-counter" id="uploadCounter">0 / 10</div>
        <button class="btn btn-secondary" onclick="cancelUpload()" style="margin-top:8px;">
            <i class="fas fa-times"></i> Cancel
        </button>
    </div>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modalOverlay">
    <div class="modal" id="modalContent"></div>
</div>

<!-- App -->
<div class="app-container">

    <!-- Sidebar -->
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-brand">
            <h2><i class="fab fa-youtube"></i> SongUploader</h2>
            <span>YouTube Trending Songs Manager</span>
        </div>
        <nav class="nav-section">
            <div class="nav-label">Main</div>
            <div class="nav-item active" data-section="dashboard" onclick="switchSection('dashboard', this)">
                <i class="fas fa-chart-pie"></i> Dashboard
            </div>
            <div class="nav-item" data-section="trending" onclick="switchSection('trending', this)">
                <i class="fas fa-fire"></i> Trending Songs
                <span class="badge">10</span>
            </div>
            <div class="nav-item" data-section="queue" onclick="switchSection('queue', this)">
                <i class="fas fa-list-ol"></i> Upload Queue
                <span class="badge" id="queueBadge">0</span>
            </div>
            <div class="nav-label" style="margin-top:12px;">Settings</div>
            <div class="nav-item" data-section="api-config" onclick="switchSection('api-config', this)">
                <i class="fas fa-key"></i> API Configuration
            </div>
            <div class="nav-item" data-section="github" onclick="switchSection('github', this)">
                <i class="fab fa-github"></i> GitHub Reference
            </div>
        </nav>
        <div class="sidebar-footer">
            <div class="user-info">
                <div class="avatar">J</div>
                <div>
                    <div class="user-name">Jasvidhani</div>
                    <div class="user-role">YouTube Creator</div>
                </div>
            </div>
        </div>
    </aside>

    <!-- Main -->
    <main class="main-content">

        <!-- ====== DASHBOARD ====== -->
        <div class="section active" id="section-dashboard">
            <div class="top-bar">
                <h1>Welcome, <span>Jasvidhani</span></h1>
                <div class="top-actions">
                    <button class="btn btn-primary" onclick="switchSection('trending', document.querySelector('[data-section=trending]'))">
                        <i class="fas fa-fire"></i> Find Trending Songs
                    </button>
                </div>
            </div>

            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-music"></i></div>
                    <div class="stat-value" id="statTotal">10</div>
                    <div class="stat-label">Trending Songs Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                    <div class="stat-value" id="statUploaded">0</div>
                    <div class="stat-label">Successfully Uploaded</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-clock"></i></div>
                    <div class="stat-value" id="statPending">0</div>
                    <div class="stat-label">Pending in Queue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-eye"></i></div>
                    <div class="stat-value">--</div>
                    <div class="stat-label">Total Views (All Time)</div>
                </div>
            </div>

            <div class="section-header">
                <h2 class="section-title">Quick Start Guide</h2>
            </div>
            <div class="config-grid">
                <div class="config-card">
                    <h3><i class="fas fa-1"></i> API Setup</h3>
                    <p>YouTube Data API v3 key और GitHub repo से API endpoints configure करें।</p>
                    <button class="btn btn-secondary btn-sm" onclick="switchSection('api-config', document.querySelector('[data-section=api-config]'))">
                        <i class="fas fa-arrow-right"></i> Go to API Config
                    </button>
                </div>
                <div class="config-card">
                    <h3><i class="fas fa-2"></i> Find Trending</h3>
                    <p>10 trending songs discover करें और अपनी queue में add करें।</p>
                    <button class="btn btn-secondary btn-sm" onclick="switchSection('trending', document.querySelector('[data-section=trending]'))">
                        <i class="fas fa-arrow-right"></i> Browse Trending
                    </button>
                </div>
                <div class="config-card">
                    <h3><i class="fas fa-3"></i> Review Queue</h3>
                    <p>Upload queue check करें, order adjust करें, titles edit करें।</p>
                    <button class="btn btn-secondary btn-sm" onclick="switchSection('queue', document.querySelector('[data-section=queue]'))">
                        <i class="fas fa-arrow-right"></i> View Queue
                    </button>
                </div>
                <div class="config-card">
                    <h3><i class="fas fa-4"></i> Start Upload</h3>
                    <p>Queue ready होने पर सभी 10 songs एक साथ upload करें।</p>
                    <button class="btn btn-primary btn-sm" onclick="startBatchUpload()">
                        <i class="fas fa-rocket"></i> Start Upload
                    </button>
                </div>
            </div>
        </div>

        <!-- ====== TRENDING SONGS ====== -->
        <div class="section" id="section-trending">
            <div class="top-bar">
                <h1>Trending <span>Songs</span></h1>
                <div class="top-actions">
                    <button class="btn btn-secondary" onclick="loadTrendingSongs()">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                    <button class="btn btn-primary" onclick="addAllToQueue()">
                        <i class="fas fa-plus-circle"></i> Add All to Queue
                    </button>
                </div>
            </div>

            <div class="search-bar">
                <div class="search-input-wrap">
                    <i class="fas fa-search"></i>
                    <input type="text" id="searchInput" placeholder="Search songs by name, artist..." oninput="filterSongs()">
                </div>
                <select class="form-input" style="width:180px;" id="regionFilter" onchange="loadTrendingSongs()">
                    <option value="IN">India (IN)</option>
                    <option value="US">United States (US)</option>
                    <option value="GB">United Kingdom (GB)</option>
                    <option value="PK">Pakistan (PK)</option>
                    <option value="BD">Bangladesh (BD)</option>
                </select>
            </div>

            <div class="songs-grid" id="songsGrid">
                <!-- Songs loaded dynamically -->
            </div>
        </div>

        <!-- ====== UPLOAD QUEUE ====== -->
        <div class="section" id="section-queue">
            <div class="top-bar">
                <h1>Upload <span>Queue</span></h1>
                <div class="top-actions">
                    <button class="btn btn-secondary" onclick="clearQueue()">
                        <i class="fas fa-trash-alt"></i> Clear Queue
                    </button>
                    <button class="btn btn-primary" id="startUploadBtn" onclick="startBatchUpload()">
                        <i class="fas fa-rocket"></i> Start Upload All
                    </button>
                </div>
            </div>

            <div class="queue-container" id="queueContainer">
                <div class="queue-header-bar">
                    <h3>
                        <i class="fas fa-list-ol" style="color:var(--accent)"></i>
                        Upload Queue
                        <span class="queue-count" id="queueCountBadge">0</span>
                    </h3>
                    <div style="display:flex;gap:8px;align-items:center;">
                        <span style="font-size:12px;color:var(--fg-muted);">Auto-advance: </span>
                        <label style="position:relative;width:40px;height:22px;cursor:pointer;">
                            <input type="checkbox" id="autoAdvance" checked style="display:none;">
                            <span id="toggleTrack" style="position:absolute;inset:0;background:var(--accent);border-radius:20px;transition:0.3s;" onclick="this.previousElementSibling.checked=!this.previousElementSibling.checked;this.style.background=this.previousElementSibling.checked?'var(--accent)':'rgba(255,255,255,0.1)'">
                                <span style="position:absolute;top:2px;left:2px;width:18px;height:18px;background:#fff;border-radius:50%;transition:0.3s;transform:translateX(18px);" id="toggleThumb"></span>
                            </span>
                        </label>
                    </div>
                </div>
                <ul class="queue-list" id="queueList">
                    <!-- Queue items dynamically -->
                </ul>
                <div class="empty-state" id="queueEmpty" style="display:none;">
                    <i class="fas fa-inbox"></i>
                    <h3>Queue is Empty</h3>
                    <p>Trending songs section से songs add करें</p>
                    <button class="btn btn-primary" style="margin-top:16px;" onclick="switchSection('trending', document.querySelector('[data-section=trending]'))">
                        <i class="fas fa-fire"></i> Browse Trending
                    </button>
                </div>
            </div>
        </div>

        <!-- ====== API CONFIG ====== -->
        <div class="section" id="section-api-config">
            <div class="top-bar">
                <h1>API <span>Configuration</span></h1>
                <div class="top-actions">
                    <button class="btn btn-secondary" onclick="testApiConnection()">
                        <i class="fas fa-plug"></i> Test Connection
                    </button>
                    <button class="btn btn-primary" onclick="saveApiConfig()">
                        <i class="fas fa-save"></i> Save Config
                    </button>
                </div>
            </div>

            <div class="config-grid">
                <div class="config-card">
                    <h3><i class="fab fa-youtube"></i> YouTube Data API v3</h3>
                    <p>Google Cloud Console से API Key generate करें</p>
                    <div class="form-group">
                        <label class="form-label">API Key</label>
                        <input type="password" class="form-input" id="ytApiKey" placeholder="AIzaSyD..." value="">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Channel ID</label>
                        <input type="text" class="form-input" id="ytChannelId" placeholder="UCxxxxxxxxxxxxxxxx">
                    </div>
                    <div class="form-hint"><i class="fas fa-exclamation-triangle"></i> API Key सुरक्षित रखें, इसे share न करें</div>
                </div>

                <div class="config-card">
                    <h3><i class="fab fa-github"></i> GitHub Repository API</h3>
                    <p>jasvidhani-star repo से API endpoints</p>
                    <div class="form-group">
                        <label class="form-label">GitHub Token</label>
                        <input type="password" class="form-input" id="ghToken" placeholder="ghp_xxxx...">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Repo Endpoint URL</label>
                        <input type="text" class="form-input" id="ghEndpoint" placeholder="https://api.github.com/repos/jasvidhani-star/..." value="https://api.github.com/repos/jasvidhani-star/youtube-uploader">
                    </div>
                    <div class="form-hint"><i class="fas fa-exclamation-triangle"></i> GitHub Personal Access Token बनाएं (repo scope)</div>
                </div>

                <div class="config-card full-width">
                    <h3><i class="fas fa-upload"></i> Upload Settings</h3>
                    <p>Video upload के default settings configure करें</p>
                    <div class="config-grid" style="gap:16px;">
                        <div class="form-group">
                            <label class="form-label">Default Title Template</label>
                            <input type="text" class="form-input" id="titleTemplate" placeholder="{song_name} - {artist} | Trending Song 2025" value="{song_name} - {artist} | Trending Song 2025">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Default Category</label>
                            <select class="form-input" id="videoCategory">
                                <option value="10">Music</option>
                                <option value="20">Gaming</option>
                                <option value="22">People & Blogs</option>
                                <option value="24">Entertainment</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Privacy Status</label>
                            <select class="form-input" id="privacyStatus">
                                <option value="public">Public</option>
                                <option value="unlisted">Unlisted</option>
                                <option value="private" selected>Private (Recommended)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Default Language</label>
                            <select class="form-input" id="videoLanguage">
                                <option value="hi" selected>Hindi</option>
                                <option value="en">English</option>
                                <option value="ur">Urdu</option>
                                <option value="bn">Bengali</option>
                            </select>
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label class="form-label">Default Tags (comma separated)</label>
                            <input type="text" class="form-input" id="defaultTags" placeholder="trending, song, new song, 2025, hindi song, music" value="trending, song, new song, 2025, hindi song, music, latest, viral, top song">
                        </div>
                        <div class="form-group" style="grid-column: 1 / -1;">
                            <label class="form-label">Default Description</label>
                            <textarea class="form-input" id="defaultDesc" placeholder="Video description...">🎧 Listen to the latest trending song!

Song: {song_name}
Artist: {artist}

🔔 Subscribe for more trending songs!
👍 Like & Share if you enjoyed!
💬 Comment your favorite part!

#trending #song #music #2025 #newrelease</textarea>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- ====== GITHUB REFERENCE ====== -->
        <div class="section" id="section-github">
            <div class="top-bar">
                <h1>GitHub <span>Reference</span></h1>
                <div class="top-actions">
                    <a href="https://github.com/jasvidhani-star" target="_blank" class="btn btn-secondary">
                        <i class="fab fa-github"></i> Open Repository
                    </a>
                </div>
            </div>

            <div class="config-grid">
                <div class="config-card full-width">
                    <h3><i class="fab fa-github" style="color:#fff"></i> Repository: jasvidhani-star</h3>
                    <p>आपके GitHub repo में मौजूद API endpoints और उनका उपयोग</p>
                </div>

                <div class="config-card">
                    <h3><i class="fas fa-code"></i> 1. Trending Songs API</h3>
                    <p>YouTube Data API से trending songs fetch करने का endpoint</p>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyCode(this)"><i class="fas fa-copy"></i> Copy</button>
<span class="code-cm">// GitHub API से trending songs fetch करें</span>
<span class="code-kw">const</span> <span class="code-fn">fetchTrending</span> = <span class="code-kw">async</span> () => {
  <span class="code-kw">const</span> region = <span class="code-str">'IN'</span>;
  <span class="code-kw">const</span> url = <span class="code-str">`https://api.github.com/repos/
    jasvidhani-star/youtube-uploader/
    contents/api/trending?ref=main`</span>;

  <span class="code-kw">const</span> res = <span class="code-kw">await</span> <span class="code-fn">fetch</span>(url, {
    headers: {
      <span class="code-str">'Authorization'</span>: <span class="code-str">`token ${GH_TOKEN}`</span>
    }
  });
  <span class="code-kw">return</span> res.<span class="code-fn">json</span>();
};
                    </div>
                </div>

                <div class="config-card">
                    <h3><i class="fas fa-upload"></i> 2. Upload Video API</h3>
                    <p>Video upload करने का GitHub Actions based endpoint</p>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyCode(this)"><i class="fas fa-copy"></i> Copy</button>
<span class="code-cm">// Video upload trigger करें</span>
<span class="code-kw">const</span> <span class="code-fn">uploadVideo</span> = <span class="code-kw">async</span> (videoData) => {
  <span class="code-kw">const</span> url = <span class="code-str">`https://api.github.com/repos/
    jasvidhani-star/youtube-uploader/
    dispatches`</span>;

  <span class="code-kw">await</span> <span class="code-fn">fetch</span>(url, {
    method: <span class="code-str">'POST'</span>,
    headers: {
      <span class="code-str">'Authorization'</span>: <span class="code-str">`token ${GH_TOKEN}`</span>,
      <span class="code-str">'Accept'</span>: <span class="code-str">'application/vnd.github.v3+json'</span>
    },
    body: JSON.<span class="code-fn">stringify</span>({
      event_type: <span class="code-str">'video_upload'</span>,
      client_payload: videoData
    })
  });
};
                    </div>
                </div>

                <div class="config-card full-width">
                    <h3><i class="fas fa-terminal"></i> 3. Complete Upload Flow (cURL)</h3>
                    <p>Terminal से सीधे upload trigger करने का पूरा command</p>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyCode(this)"><i class="fas fa-copy"></i> Copy</button>
<span class="code-cm"># Step 1: Trending songs fetch करें</span>
curl -H <span class="code-str">"Authorization: token YOUR_GH_TOKEN"</span> \
  <span class="code-str">"https://api.github.com/repos/jasvidhani-star/youtube-uploader/contents/api/trending"</span>

<span class="code-cm"># Step 2: Upload dispatch trigger करें</span>
curl -X POST \
  -H <span class="code-str">"Authorization: token YOUR_GH_TOKEN"</span> \
  -H <span class="code-str">"Accept: application/vnd.github.v3+json"</span> \
  -d <span class="code-str">'{
    "event_type": "video_upload",
    "client_payload": {
      "video_url": "https://example.com/song.mp4",
      "title": "Song Name - Artist | Trending 2025",
      "description": "Listen to...",
      "tags": ["trending", "song"],
      "category": "10",
      "privacy": "private"
    }
  }'</span> \
  <span class="code-str">"https://api.github.com/repos/jasvidhani-star/youtube-uploader/dispatches"</span>

<span class="code-cm"># Step 3: Upload status check करें</span>
curl -H <span class="code-str">"Authorization: token YOUR_GH_TOKEN"</span> \
  <span class="code-str">"https://api.github.com/repos/jasvidhani-star/youtube-uploader/actions/runs?per_page=5"</span>
                    </div>
                </div>

                <div class="config-card full-width">
                    <h3><i class="fas fa-file-code"></i> 4. GitHub Actions Workflow Structure</h3>
                    <p>आपके repo में होना चाहिए ये workflow file</p>
                    <div class="code-block">
                        <button class="copy-btn" onclick="copyCode(this)"><i class="fas fa-copy"></i> Copy</button>
<span class="code-cm"># .github/workflows/upload-video.yml</span>
<span class="code-kw">name</span>: Upload Video to YouTube

<span class="code-kw">on</span>:
  <span class="code-kw">repository_dispatch</span>:
    <span class="code-kw">types</span>: [video_upload]

<span class="code-kw">jobs</span>:
  <span class="code-kw">upload</span>:
    <span class="code-kw">runs-on</span>: ubuntu-latest
    <span class="code-kw">steps</span>:
      - <span class="code-kw">uses</span>: actions/checkout@v4

      - <span class="code-kw">name</span>: Download Video
        <span class="code-kw">run</span>: |
          wget <span class="code-str">"${{ github.event.client_payload.video_url }}"</span> \
            -O video.mp4

      - <span class="code-kw">name</span>: Upload to YouTube
        <span class="code-kw">uses</span>: tokyoneon/youtube-upload@<span class="code-num">v1</span>
        <span class="code-kw">with</span>:
          credentials: <span class="code-str">${{ secrets.YT_OAUTH }}</span>
          video: video.mp4
          title: <span class="code-str">${{ github.event.client_payload.title }}</span>
          description: <span class="code-str">${{ github.event.client_payload.description }}</span>
          category: <span class="code-str">${{ github.event.client_payload.category }}</span>
          tags: <span class="code-str">${{ github.event.client_payload.tags }}</span>
          privacy: <span class="code-str">${{ github.event.client_payload.privacy }}</span>
                    </div>
                </div>
            </div>
        </div>

    </main>
</div>

<script>
    // ============================================
    // डेटा: 10 Trending Songs (simulated)
    // ============================================
    const trendingSongsData = [
        {
            id: 1, title: "Pehle Bhi Main", artist: "Vishal Mishra, Sachin-Jigar",
            views: "285M", duration: "4:12", region: "IN",
            thumb: "https://picsum.photos/seed/song1/400/250.jpg",
            category: "Bollywood", trending: "#1"
        },
        {
            id: 2, title: "Satranga", artist: "Arijit Singh, Shreya Ghoshal",
            views: "412M", duration: "3:58", region: "IN",
            thumb: "https://picsum.photos/seed/song2/400/250.jpg",
            category: "Romantic", trending: "#2"
        },
        {
            id: 3, title: "Heeriye", artist: "Jasleen Royal, Arijit Singh",
            views: "520M", duration: "3:45", region: "IN",
            thumb: "https://picsum.photos/seed/song3/400/250.jpg",
            category: "Pop", trending: "#3"
        },
        {
            id: 4, title: "Chaleya", artist: "Arijit Singh, Shilpa Rao",
            views: "380M", duration: "4:22", region: "IN",
            thumb: "https://picsum.photos/seed/song4/400/250.jpg",
            category: "Bollywood", trending: "#4"
        },
        {
            id: 5, title: "Maan Meri Jaan", artist: "King",
            views: "890M", duration: "3:32", region: "IN",
            thumb: "https://picsum.photos/seed/song5/400/250.jpg",
            category: "Hip-Hop", trending: "#5"
        },
        {
            id: 6, title: "Pasoori Nu", artist: "Ali Sethi, Shae Gill",
            views: "750M", duration: "3:57", region: "IN",
            thumb: "https://picsum.photos/seed/song6/400/250.jpg",
            category: "Fusion", trending: "#6"
        },
        {
            id: 7, title: "Kya Baat Hai 2.0", artist: "Hardy Sandhu, Neha Kakkar",
            views: "340M", duration: "3:28", region: "IN",
            thumb: "https://picsum.photos/seed/song7/400/250.jpg",
            category: "Punjabi", trending: "#7"
        },
        {
            id: 8, title: "O Maahi", artist: "Pritam, Arijit Singh",
            views: "210M", duration: "4:05", region: "IN",
            thumb: "https://picsum.photos/seed/song8/400/250.jpg",
            category: "Bollywood", trending: "#8"
        },
        {
            id: 9, title: "Soulmate", artist: "Badshah, Arijit Singh",
            views: "195M", duration: "3:41", region: "IN",
            thumb: "https://picsum.photos/seed/song9/400/250.jpg",
            category: "Pop", trending: "#9"
        },
        {
            id: 10, title: "Angaaron", artist: "Shilpa Rao, Vishal-Shekhar",
            views: "265M", duration: "4:33", region: "IN",
            thumb: "https://picsum.photos/seed/song10/400/250.jpg",
            category: "Bollywood", trending: "#10"
        }
    ];

    // ============================================
    // State Management
    // ============================================
    let uploadQueue = [];
    let isUploading = false;
    let uploadCancelled = false;

    // ============================================
    // Navigation
    // ============================================
    function switchSection(sectionId, navEl) {
        // सभी sections छुपाएं
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

        // चुना हुआ section दिखाएं
        const section = document.getElementById('section-' + sectionId);
        if (section) section.classList.add('active');
        if (navEl) navEl.classList.add('active');

        // Mobile पर sidebar बंद करें
        document.querySelector('.sidebar').classList.remove('open');
    }

    // ============================================
    // Trending Songs Rendering
    // ============================================
    function loadTrendingSongs() {
        const grid = document.getElementById('songsGrid');
        grid.innerHTML = '';

        const searchTerm = (document.getElementById('searchInput').value || '').toLowerCase();
        const region = document.getElementById('regionFilter').value;

        let filtered = trendingSongsData.filter(s => {
            const matchSearch = !searchTerm ||
                s.title.toLowerCase().includes(searchTerm) ||
                s.artist.toLowerCase().includes(searchTerm);
            const matchRegion = s.region === region;
            return matchSearch && matchRegion;
        });

        if (filtered.length === 0) {
            grid.innerHTML = `
                <div class="empty-state" style="grid-column:1/-1;">
                    <i class="fas fa-search"></i>
                    <h3>No Songs Found</h3>
                    <p>कृपया अलग search term या region try करें</p>
                </div>
            `;
            return;
        }

        filtered.forEach((song, idx) => {
            const inQueue = uploadQueue.some(q => q.id === song.id);
            const card = document.createElement('div');
            card.className = 'song-card';
            card.setAttribute('data-song-id', song.id);
            card.innerHTML = `
                <div class="song-thumb-wrap">
                    <span class="song-rank">${song.trending}</span>
                    <img class="song-thumb" src="${song.thumb}" alt="${song.title}" loading="lazy">
                    <span class="song-duration"><i class="fas fa-clock" style="margin-right:3px;font-size:9px;"></i>${song.duration}</span>
                </div>
                <div class="song-info">
                    <div class="song-title" title="${song.title}">${song.title}</div>
                    <div class="song-artist"><i class="fas fa-user" style="font-size:10px;"></i> ${song.artist}</div>
                    <div class="song-meta">
                        <span><i class="fas fa-eye"></i> ${song.views} views</span>
                        <span><i class="fas fa-tag"></i> ${song.category}</span>
                    </div>
                    <div class="song-actions">
                        <button class="btn btn-sm ${inQueue ? 'btn-added' : 'btn-add'}" 
                            onclick="${inQueue ? `removeFromQueue(${song.id})` : `addToQueue(${song.id})`}"
                            id="addBtn-${song.id}">
                            <i class="fas ${inQueue ? 'fa-check' : 'fa-plus'}"></i>
                            ${inQueue ? 'In Queue' : 'Add to Queue'}
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="previewSong(${song.id})">
                            <i class="fas fa-play"></i>
                        </button>
                    </div>
                </div>
            `;
            // Staggered animation
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = `opacity 0.4s ease ${idx * 0.06}s, transform 0.4s ease ${idx * 0.06}s`;
            grid.appendChild(card);
            requestAnimationFrame(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            });
        });
    }

    function filterSongs() {
        loadTrendingSongs();
    }

    // ============================================
    // Queue Management
    // ============================================
    function addToQueue(songId) {
        const song = trendingSongsData.find(s => s.id === songId);
        if (!song || uploadQueue.some(q => q.id === songId)) return;

        // Title template apply करें
        const template = document.getElementById('titleTemplate').value || '{song_name} - {artist}';
        const finalTitle = template
            .replace('{song_name}', song.title)
            .replace('{artist}', song.artist);

        uploadQueue.push({
            ...song,
            finalTitle: finalTitle,
            status: 'pending',
            progress: 0
        });

        showToast('success', `"${song.title}" queue में add हो गया`);
        updateQueueUI();
        updateSongButton(songId, true);
        updateStats();
    }

    function removeFromQueue(songId) {
        const song = uploadQueue.find(q => q.id === songId);
        uploadQueue = uploadQueue.filter(q => q.id !== songId);
        if (song) showToast('info', `"${song.title}" queue से हटाया गया`);
        updateQueueUI();
        updateSongButton(songId, false);
        updateStats();
    }

    function addAllToQueue() {
        let added = 0;
        trendingSongsData.forEach(song => {
            if (!uploadQueue.some(q => q.id === song.id)) {
                const template = document.getElementById('titleTemplate').value || '{song_name} - {artist}';
                const finalTitle = template
                    .replace('{song_name}', song.title)
                    .replace('{artist}', song.artist);
                uploadQueue.push({
                    ...song,
                    finalTitle: finalTitle,
                    status: 'pending',
                    progress: 0
                });
                added++;
            }
        });
        if (added > 0) {
            showToast('success', `${added} songs queue में add हुए`);
        } else {
            showToast('info', 'सभी songs पहले से queue में हैं');
        }
        loadTrendingSongs();
        updateQueueUI();
        updateStats();
    }

    function clearQueue() {
        if (uploadQueue.length === 0) return;
        if (isUploading) {
            showToast('error', 'Upload चल रहा है, पहले cancel करें');
            return;
        }
        showModal('Clear Queue', 'क्या आप सभी songs queue से हटाना चाहते हैं?', () => {
            const ids = uploadQueue.map(q => q.id);
            uploadQueue = [];
            ids.forEach(id => updateSongButton(id, false));
            updateQueueUI();
            updateStats();
            showToast('info', 'Queue clear हो गया');
        });
    }

    function updateSongButton(songId, inQueue) {
        const btn = document.getElementById('addBtn-' + songId);
        if (!btn) return;
        if (inQueue) {
            btn.className = 'btn btn-sm btn-added';
            btn.innerHTML = '<i class="fas fa-check"></i> In Queue';
            btn.onclick = () => removeFromQueue(songId);
        } else {
            btn.className = 'btn btn-sm btn-add';
            btn.innerHTML = '<i class="fas fa-plus"></i> Add to Queue';
            btn.onclick = () => addToQueue(songId);
        }
    }

    function updateQueueUI() {
        const list = document.getElementById('queueList');
        const empty = document.getElementById('queueEmpty');
        const countBadge = document.getElementById('queueCountBadge');
        const qBadge = document.getElementById('queueBadge');

        countBadge.textContent = uploadQueue.length;
        qBadge.textContent = uploadQueue.length;

        if (uploadQueue.length === 0) {
            list.innerHTML = '';
            empty.style.display = 'block';
            return;
        }

        empty.style.display = 'none';
        list.innerHTML = '';

        uploadQueue.forEach((song, idx) => {
            const li = document.createElement('li');
            li.className = 'queue-item';

            const statusClass = song.status === 'complete' ? 'status-complete' :
                               song.status === 'uploading' ? 'status-uploading' :
                               song.status === 'error' ? 'status-error' : 'status-pending';

            const statusText = song.status === 'complete' ? '<i class="fas fa-check-circle"></i> Complete' :
                              song.status === 'uploading' ? '<span class="spinner"></span> Uploading' :
                              song.status === 'error' ? '<i class="fas fa-times-circle"></i> Error' :
                              '<i class="fas fa-clock"></i> Pending';

            const progressClass = song.status === 'complete' ? 'complete' :
                                 song.status === 'error' ? 'error' : '';

            li.innerHTML = `
                <span class="queue-num">${idx + 1}</span>
                <img class="queue-thumb" src="${song.thumb}" alt="" loading="lazy">
                <div class="queue-song-info">
                    <div class="q-title" title="${song.finalTitle}">${song.finalTitle}</div>
                    <div class="q-artist">${song.artist} &middot; ${song.duration}</div>
                </div>
                <div class="progress-wrap">
                    <div class="progress-label">
                        <span>Progress</span>
                        <span>${song.progress}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill ${progressClass}" style="width:${song.progress}%"></div>
                    </div>
                </div>
                <span class="status-badge ${statusClass}">${statusText}</span>
                <div class="queue-item-actions">
                    ${song.status === 'pending' ? `<button class="btn-icon" title="Remove" onclick="removeFromQueue(${song.id})"><i class="fas fa-trash-alt" style="font-size:12px;"></i></button>` : ''}
                    ${song.status === 'error' ? `<button class="btn-icon" title="Retry" onclick="retrySong(${song.id})"><i class="fas fa-redo" style="font-size:12px;"></i></button>` : ''}
                </div>
            `;
            list.appendChild(li);
        });
    }

    function retrySong(songId) {
        const song = uploadQueue.find(q => q.id === songId);
        if (song) {
            song.status = 'pending';
            song.progress = 0;
            updateQueueUI();
            showToast('info', `"${song.title}" retry queue में add हुआ`);
        }
    }

    // ============================================
    // Upload Simulation
    // ============================================
    function startBatchUpload() {
        if (isUploading) {
            showToast('warning', 'Upload already चल रहा है');
            return;
        }

        const pending = uploadQueue.filter(q => q.status === 'pending' || q.status === 'error');
        if (pending.length === 0) {
            showToast('warning', 'Queue में कोई pending song नहीं है');
            return;
        }

        // API config check
        const apiKey = document.getElementById('ytApiKey').value;
        const ghToken = document.getElementById('ghToken').value;
        if (!apiKey && !ghToken) {
            showModal('API Keys Required',
                'YouTube API Key या GitHub Token configure नहीं है। बिना keys के simulation mode में run होगा। क्या आप जारी रखना चाहते हैं?',
                () => runUploadSequence(pending)
            );
            return;
        }

        runUploadSequence(pending);
    }

    async function runUploadSequence(songs) {
        isUploading = true;
        uploadCancelled = false;
        const overlay = document.getElementById('uploadOverlay');
        overlay.classList.add('show');

        const ring = document.getElementById('uploadRing');
        const percentEl = document.getElementById('uploadPercent');
        const songNameEl = document.getElementById('uploadSongName');
        const counterEl = document.getElementById('uploadCounter');
        const circumference = 2 * Math.PI * 65; // ~408

        let completed = 0;
        const total = songs.length;

        for (let i = 0; i < songs.length; i++) {
            if (uploadCancelled) break;

            const song = uploadQueue.find(q => q.id === songs[i].id);
            if (!song) continue;

            song.status = 'uploading';
            song.progress = 0;
            updateQueueUI();

            songNameEl.textContent = song.title;
            counterEl.textContent = `${i + 1} / ${total}`;

            // Simulate upload progress
            for (let p = 0; p <= 100; p += Math.floor(Math.random() * 8) + 2) {
                if (uploadCancelled) break;
                const actualP = Math.min(p, 100);
                song.progress = actualP;

                // Update circle
                const offset = circumference - (actualP / 100) * circumference;
                ring.style.strokeDashoffset = offset;
                percentEl.textContent = actualP + '%';

                updateQueueUI();
                await sleep(150 + Math.random() * 200);
            }

            if (uploadCancelled) {
                song.status = 'error';
                song.progress = 0;
                updateQueueUI();
                break;
            }

            song.progress = 100;
            song.status = 'complete';
            completed++;
            updateQueueUI();
            updateStats();

            // अगले song से पहले थोड़ा delay
            if (i < songs.length - 1) {
                await sleep(800);
            }
        }

        // Upload complete
        ring.style.strokeDashoffset = 0;
        percentEl.textContent = '100%';

        if (!uploadCancelled) {
            songNameEl.textContent = 'All Done!';
            counterEl.textContent = `${completed} / ${total} uploaded`;
            showToast('success', `${completed} songs successfully upload हो गए!`);
        } else {
            songNameEl.textContent = 'Cancelled';
            showToast('warning', 'Upload cancel किया गया');
        }

        await sleep(2000);
        overlay.classList.remove('show');
        isUploading = false;
        updateStats();
    }

    function cancelUpload() {
        uploadCancelled = true;
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // ============================================
    // Preview Song (Modal)
    // ============================================
    function previewSong(songId) {
        const song = trendingSongsData.find(s => s.id === songId);
        if (!song) return;

        const inQueue = uploadQueue.some(q => q.id === songId);
        const template = document.getElementById('titleTemplate').value || '{song_name} - {artist}';
        const finalTitle = template
            .replace('{song_name}', song.title)
            .replace('{artist}', song.artist);

        const desc = document.getElementById('defaultDesc').value
            .replace('{song_name}', song.title)
            .replace('{artist}', song.artist);

        const modal = document.getElementById('modalContent');
        modal.innerHTML = `
            <div style="display:flex;gap:16px;margin-bottom:20px;">
                <img src="${song.thumb}" style="width:120px;height:75px;object-fit:cover;border-radius:8px;flex-shrink:0;">
                <div>
                    <h3 style="margin-bottom:4px;">${song.title}</h3>
                    <p style="margin-bottom:0;font-size:12px;">${song.artist} &middot; ${song.duration} &middot; ${song.views} views</p>
                </div>
            </div>
            <div style="margin-bottom:14px;">
                <label class="form-label">Upload Title</label>
                <input type="text" class="form-input" value="${finalTitle}" id="previewTitle">
            </div>
            <div style="margin-bottom:14px;">
                <label class="form-label">Description Preview</label>
                <textarea class="form-input" rows="4" readonly style="font-size:12px;">${desc}</textarea>
            </div>
            <div class="modal-actions">
                <button class="btn btn-ghost" onclick="closeModal()">Close</button>
                ${inQueue ?
                    `<button class="btn btn-secondary" onclick="removeFromQueue(${songId});closeModal();">Remove from Queue</button>` :
                    `<button class="btn btn-primary" onclick="addToQueue(${songId});closeModal();"><i class="fas fa-plus"></i> Add to Queue</button>`
                }
            </div>
        `;
        document.getElementById('modalOverlay').classList.add('show');
    }

    // ============================================
    // API Config
    // ============================================
    function saveApiConfig() {
        const apiKey = document.getElementById('ytApiKey').value;
        const ghToken = document.getElementById('ghToken').value;
        const channelId = document.getElementById('ytChannelId').value;

        // LocalStorage में save करें (note: production में ये secure नहीं है)
        try {
            localStorage.setItem('yt_config', JSON.stringify({
                apiKey: btoa(apiKey),
                ghToken: btoa(ghToken),
                channelId: channelId,
                endpoint: document.getElementById('ghEndpoint').value,
                titleTemplate: document.getElementById('titleTemplate').value,
                category: document.getElementById('videoCategory').value,
                privacy: document.getElementById('privacyStatus').value,
                language: document.getElementById('videoLanguage').value,
                tags: document.getElementById('defaultTags').value,
                description: document.getElementById('defaultDesc').value
            }));
            showToast('success', 'API Configuration save हो गया');
        } catch (e) {
            showToast('error', 'Config save करने में error: ' + e.message);
        }
    }

    function loadApiConfig() {
        try {
            const saved = JSON.parse(localStorage.getItem('yt_config'));
            if (saved) {
                document.getElementById('ytApiKey').value = atob(saved.apiKey || '');
                document.getElementById('ghToken').value = atob(saved.ghToken || '');
                document.getElementById('ytChannelId').value = saved.channelId || '';
                document.getElementById('ghEndpoint').value = saved.endpoint || '';
                document.getElementById('titleTemplate').value = saved.titleTemplate || '{song_name} - {artist} | Trending Song 2025';
                document.getElementById('videoCategory').value = saved.category || '10';
                document.getElementById('privacyStatus').value = saved.privacy || 'private';
                document.getElementById('videoLanguage').value = saved.language || 'hi';
                document.getElementById('defaultTags').value = saved.tags || '';
                document.getElementById('defaultDesc').value = saved.description || '';
            }
        } catch (e) { /* ignore */ }
    }

    async function testApiConnection() {
        const apiKey = document.getElementById('ytApiKey').value;
        showToast('info', 'API connection test हो रहा है...');

        if (apiKey) {
            try {
                const res = await fetch(`https://www.googleapis.com/youtube/v3/channels?part=id&key=${apiKey}&maxResults=1`);
                if (res.ok) {
                    showToast('success', 'YouTube API connection successful!');
                } else {
                    const err = await res.json();
                    showToast('error', `YouTube API Error: ${err.error?.message || 'Unknown error'}`);
                }
            } catch (e) {
                showToast('error', 'Network error: ' + e.message);
            }
        } else {
            showToast('warning', 'पहले API Key enter करें');
        }
    }

    // ============================================
    // Stats Update
    // ============================================
    function updateStats() {
        const total = trendingSongsData.length;
        const uploaded = uploadQueue.filter(q => q.status === 'complete').length;
        const pending = uploadQueue.filter(q => q.status === 'pending' || q.status === 'error').length;

        animateCounter('statTotal', total);
        animateCounter('statUploaded', uploaded);
        animateCounter('statPending', pending);
    }

    function animateCounter(id, target) {
        const el = document.getElementById(id);
        const current = parseInt(el.textContent) || 0;
        if (current === target) return;

        const diff = target - current;
        const steps = Math.min(Math.abs(diff), 20);
        const stepVal = diff / steps;
        let step = 0;

        const interval = setInterval(() => {
            step++;
            if (step >= steps) {
                el.textContent = target;
                clearInterval(interval);
            } else {
                el.textContent = Math.round(current + stepVal * step);
            }
        }, 30);
    }

    // ============================================
    // Toast Notifications
    // ============================================
    function showToast(type, message) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        const colors = {
            success: 'var(--success)',
            error: 'var(--error)',
            warning: 'var(--warning)',
            info: 'var(--info)'
        };

        toast.innerHTML = `
            <i class="fas ${icons[type]}" style="color:${colors[type]};font-size:16px;"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('hiding');
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // ============================================
    // Modal
    // ============================================
    function showModal(title, message, onConfirm) {
        const modal = document.getElementById('modalContent');
        modal.innerHTML = `
            <h3>${title}</h3>
            <p>${message}</p>
            <div class="modal-actions">
                <button class="btn btn-ghost" onclick="closeModal()">Cancel</button>
                <button class="btn btn-primary" id="modalConfirmBtn">Confirm</button>
            </div>
        `;
        document.getElementById('modalConfirmBtn').onclick = () => {
            closeModal();
            if (onConfirm) onConfirm();
        };
        document.getElementById('modalOverlay').classList.add('show');
    }

    function closeModal() {
        document.getElementById('modalOverlay').classList.remove('show');
    }

    // ESC से modal बंद
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    // Modal overlay click से बंद
    document.getElementById('modalOverlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeModal();
    });

    // ============================================
    // Copy Code
    // ============================================
    function copyCode(btn) {
        const codeBlock = btn.parentElement;
        const text = codeBlock.textContent.replace('Copy', '').trim();
        navigator.clipboard.writeText(text).then(() => {
            btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            setTimeout(() => {
                btn.innerHTML = '<i class="fas fa-copy"></i> Copy';
            }, 2000);
        });
    }

    // ============================================
    // Floating Music Notes
    // ============================================
    function createFloatingNotes() {
        const container = document.getElementById('floatingNotes');
        const notes = ['♪', '♫', '♬', '♩', '🎵'];

        for (let i = 0; i < 12; i++) {
            const note = document.createElement('span');
            note.className = 'note';
            note.textContent = notes[Math.floor(Math.random() * notes.length)];
            note.style.left = Math.random() * 100 + '%';
            note.style.fontSize = (14 + Math.random() * 18) + 'px';
            note.style.animationDuration = (6 + Math.random() * 8) + 's';
            note.style.animationDelay = (Math.random() * 10) + 's';
            note.style.opacity = '0';
            container.appendChild(note);
        }
    }

    // ============================================
    // Toggle Switch Fix
    // ============================================
    function initToggle() {
        const toggle = document.getElementById('autoAdvance');
        const track = document.getElementById('toggleTrack');
        const thumb = document.getElementById('toggleThumb');

        function updateToggle() {
            if (toggle.checked) {
                track.style.background = 'var(--accent)';
                thumb.style.transform = 'translateX(18px)';
            } else {
                track.style.background = 'rgba(255,255,255,0.1)';
                thumb.style.transform = 'translateX(0)';
            }
        }

        toggle.addEventListener('change', updateToggle);
        updateToggle();
    }

    // ============================================
    // Initialize
    // ============================================
    document.addEventListener('DOMContentLoaded', () => {
        loadApiConfig();
        loadTrendingSongs();
        updateQueueUI();
        updateStats();
        createFloatingNotes();
        initToggle();
    });
</script>
</body>
</html>
