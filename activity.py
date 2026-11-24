import os
import socketserver
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>POV: In Your DM - 장난이라는 이름의 폭력</title>
  <!-- 영문 귀여운 폰트(Quicksand, Nunito) + 손글씨 후보 10종 + 한글 웹폰트(Pretendard, Gmarket Sans) -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Dongle:wght@400;700&family=Gaegu:wght@400;700&family=Gamja+Flower&family=Gowun+Batang&family=Gowun+Dodum&family=Hi+Melody&family=Jua&family=Nanum+Pen+Script&family=Nunito:wght@400;500;600&family=Poor+Story&family=Quicksand:wght@500;600&family=Single+Day&display=swap" rel="stylesheet">
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <link href="https://webfontworld.github.io/gmarket/GmarketSans.css" rel="stylesheet" />
  <style>
    :root {
      --bg-main: #FFFDF7;
      --bg-card: #FFFFFF;
      --bg-butter: #FFF6D6;
      --bg-butter-accent: #FBE39D;
      --bg-soft: #FAF7EE;
      --text-primary: #2D2A26;
      --text-secondary: #5C564E;
      --text-muted: #8E8677;
      /* 카카오톡 스타일 파스텔 톤 채팅방 컬러 */
      --kakao-bg: #DCE6F2;
      --kakao-header: #D2DFEE;
      --kakao-my-bubble: #FEE500;
      --kakao-other-bubble: #FFFFFF;
      --kakao-unread: #D98A00;
      --border-light: #EFEAD8;
      --border-butter: #F5D67B;
      --danger: #D94E5C;
      --danger-bg: #FFF3F4;
      --success: #228B5B;
      --success-bg: #EFFAF4;
      --shadow-card: 0 14px 36px rgba(92, 78, 45, 0.08);
      --shadow-float: 0 8px 24px rgba(92, 78, 45, 0.14);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Quicksand', 'Nunito', 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif;
      font-weight: 400;
    }

    body {
      background-color: var(--bg-main);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 16px;
      font-size: 17px;
      line-height: 1.65;
    }

    /* 메인 앱 컨테이너 */
    .app-container {
      width: 100%;
      max-width: 500px;
      background: var(--bg-card);
      border-radius: 30px;
      box-shadow: var(--shadow-card);
      border: 1.5px solid var(--border-light);
      overflow: hidden;
      position: relative;
      min-height: 720px;
      display: flex;
      flex-direction: column;
    }

    /* 상단 진행 바 */
    .top-bar {
      padding: 16px 24px;
      background: var(--bg-card);
      border-bottom: 1px solid var(--border-light);
      display: none;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      z-index: 10;
    }

    .step-label {
      font-size: 14px;
      color: var(--text-secondary);
      letter-spacing: 0.04em;
    }

    .progress-track {
      flex: 1;
      height: 8px;
      background: var(--bg-soft);
      border-radius: 999px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      width: 0%;
      background: var(--bg-butter-accent);
      border-radius: 999px;
      transition: width 0.4s ease;
    }

    /* 화면 전환 */
    .screen {
      display: none;
      padding: 32px 26px;
      flex: 1;
      flex-direction: column;
      animation: fadeIn 0.35s ease;
    }

    .screen.active {
      display: flex;
    }

    /* 카톡 채팅방 전용 패딩 초기화 */
    #screenChat {
      padding: 0;
      background: var(--kakao-bg);
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      20%, 60% { transform: translateX(-6px); }
      40%, 80% { transform: translateX(6px); }
    }

    @keyframes notiPop {
      0% { opacity: 0; transform: translateY(-16px) scale(0.95); }
      65% { opacity: 1; transform: translateY(3px) scale(1.01); }
      100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    .noti-pop-anim {
      animation: notiPop 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }

    .shake {
      animation: shake 0.35s ease;
    }

    /* 타이틀 및 타이포그래피 */
    .title-display {
      font-family: 'Quicksand', 'GmarketSans', 'Pretendard', sans-serif;
      font-weight: 600;
      font-size: 33px;
      line-height: 1.3;
      color: var(--text-primary);
      letter-spacing: -0.01em;
    }

    .subtitle-display {
      font-size: 20px;
      color: var(--text-secondary);
      margin-top: 8px;
      line-height: 1.5;
    }

    /* 1. 시작 화면 */
    .intro-hero {
      margin-top: 24px;
      margin-bottom: 32px;
      text-align: center;
    }

    /* 교사용 은은한 비밀 진입 아이콘 (첫 화면 우측 상단) */
    .secret-teacher-btn {
      position: absolute;
      top: 14px;
      right: 16px;
      width: 30px;
      height: 30px;
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 13px;
      opacity: 0.25;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: opacity 0.2s ease, background 0.2s ease;
      z-index: 5;
    }

    .secret-teacher-btn:hover {
      opacity: 0.65;
      background: var(--bg-soft);
    }

    .tutor-intro-card {
      background: var(--bg-butter);
      border: 1.5px solid var(--border-butter);
      border-radius: 22px;
      padding: 20px 22px;
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 32px;
    }

    .tutor-emoji-badge {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: #FFFFFF;
      border: 1.5px solid var(--border-butter);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 30px;
      flex-shrink: 0;
      box-shadow: 0 4px 10px rgba(180, 145, 50, 0.12);
    }

    .tutor-intro-text {
      font-size: 16px;
      color: var(--text-primary);
      line-height: 1.6;
    }

    .input-group {
      margin-bottom: 24px;
    }

    .input-label {
      display: block;
      font-size: 16px;
      color: var(--text-primary);
      margin-bottom: 10px;
    }

    .text-input {
      width: 100%;
      padding: 16px 18px;
      font-size: 18px;
      border: 1.5px solid var(--border-light);
      border-radius: 16px;
      background: #FFFFFF;
      color: var(--text-primary);
      outline: none;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .text-input:focus {
      border-color: var(--border-butter);
      box-shadow: 0 0 0 4px rgba(251, 227, 157, 0.35);
    }

    .error-msg {
      color: var(--danger);
      font-size: 15px;
      margin-top: 8px;
      min-height: 22px;
    }

    /* 버튼 공통 */
    .btn-primary {
      width: 100%;
      padding: 18px 24px;
      font-size: 18px;
      background: var(--bg-butter-accent);
      color: var(--text-primary);
      border: 1.5px solid var(--border-butter);
      border-radius: 18px;
      cursor: pointer;
      transition: background 0.2s ease, transform 0.1s ease;
      margin-top: auto;
    }

    .btn-primary:hover {
      background: #F9D97A;
    }

    .btn-primary:active {
      transform: scale(0.99);
    }

    .btn-secondary {
      width: 100%;
      padding: 15px 20px;
      font-size: 16px;
      background: var(--bg-soft);
      color: var(--text-primary);
      border: 1.5px solid var(--border-light);
      border-radius: 16px;
      cursor: pointer;
      transition: background 0.2s ease;
    }

    .btn-secondary:hover {
      background: var(--bg-butter);
    }

    /* 2. SCENARIO 화면 */
    .scenario-badge {
      display: inline-block;
      padding: 6px 14px;
      background: var(--bg-butter);
      border: 1px solid var(--border-butter);
      color: var(--text-primary);
      border-radius: 999px;
      font-size: 14px;
      letter-spacing: 0.08em;
      margin-bottom: 16px;
      align-self: flex-start;
    }

    .phone-notification {
      background: #FFFFFF;
      border: 1.5px solid var(--border-butter);
      border-radius: 22px;
      padding: 18px 20px;
      margin: 18px 0 22px;
      box-shadow: 0 10px 26px rgba(92, 78, 45, 0.12);
    }

    .noti-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13.5px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }

    .noti-app-tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #FEE500;
      color: #2D2A26;
      padding: 3px 10px;
      border-radius: 999px;
      font-size: 12.5px;
      font-weight: 500;
    }

    .noti-body {
      font-size: 16.5px;
      color: var(--text-primary);
      line-height: 1.6;
    }

    .learning-takeaway-box {
      background: #FFFFFF;
      border: 1.5px solid var(--border-butter);
      border-radius: 18px;
      padding: 16px 18px;
      margin-top: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .takeaway-item {
      font-size: 15.5px;
      color: var(--text-primary);
      line-height: 1.6;
    }

    .takeaway-badge {
      display: inline-block;
      background: var(--bg-butter);
      border: 1px solid var(--border-butter);
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 13px;
      margin-bottom: 4px;
      color: var(--text-primary);
    }

    /* 핵심 이론 텍스트 연노랑 형광펜 스타일 */
    .theory-text-underline {
      background: linear-gradient(180deg, transparent 54%, #FFF3B8 54%, #FFF3B8 90%, transparent 90%);
      padding: 1px 4px;
      border-radius: 4px;
      box-decoration-break: clone;
      -webkit-box-decoration-break: clone;
      color: var(--text-primary);
    }

    .scenario-desc {
      font-size: 17px;
      color: var(--text-secondary);
      line-height: 1.75;
      margin-bottom: 24px;
    }

    /* 3. 실제 카카오톡 스타일 메신저 화면 */
    .kakao-header {
      background: var(--kakao-header);
      padding: 14px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    }

    .kakao-header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .kakao-back-icon {
      font-size: 20px;
      color: #2B333E;
      line-height: 1;
    }

    .kakao-room-title {
      font-size: 18px;
      font-weight: 500;
      color: #1E242B;
    }

    .kakao-room-sub {
      font-size: 12.5px;
      color: #536273;
    }

    .kakao-header-icons {
      display: flex;
      gap: 12px;
      font-size: 17px;
      color: #2B333E;
    }

    .chat-area {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 14px;
      padding: 16px 16px 12px;
      overflow-y: auto;
      max-height: 310px;
    }

    .kakao-date-pill {
      align-self: center;
      background: rgba(65, 82, 102, 0.18);
      color: #FFFFFF;
      font-size: 12.5px;
      padding: 4px 14px;
      border-radius: 999px;
      margin-bottom: 4px;
    }

    .typing-indicator {
      align-self: flex-start;
      background: rgba(255, 255, 255, 0.85);
      padding: 10px 16px;
      border-radius: 18px;
      font-size: 14px;
      color: #5A6777;
      display: none;
    }

    /* 상대방(민수) 카톡 메시지 행 */
    .kakao-msg-row.other {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      animation: fadeIn 0.3s ease;
    }

    .kakao-profile-pic {
      width: 40px;
      height: 40px;
      border-radius: 15px;
      background: #FFFFFF;
      border: 1px solid rgba(0, 0, 0, 0.08);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      flex-shrink: 0;
    }

    .kakao-msg-col {
      display: flex;
      flex-direction: column;
      max-width: 82%;
    }

    .kakao-sender-name {
      font-size: 13px;
      color: #3D4A59;
      margin-bottom: 4px;
      margin-left: 2px;
    }

    .kakao-bubble-line {
      display: flex;
      align-items: flex-end;
      gap: 6px;
    }

    .kakao-bubble.other {
      position: relative;
      background: var(--kakao-other-bubble);
      color: #1E2024;
      padding: 12px 15px;
      border-radius: 16px;
      border-top-left-radius: 4px;
      font-family: 'Nunito', 'Quicksand', 'Pretendard', sans-serif;
      font-weight: 500;
      font-size: 16.5px;
      line-height: 1.55;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
    }

    /* 내 카톡 메시지 행 */
    .kakao-msg-row.me {
      display: flex;
      justify-content: flex-end;
      align-items: flex-end;
      gap: 6px;
      animation: fadeIn 0.3s ease;
    }

    .kakao-bubble.me {
      max-width: 78%;
      background: var(--kakao-my-bubble);
      color: #1E2024;
      padding: 12px 15px;
      border-radius: 16px;
      border-top-right-radius: 4px;
      font-family: 'Nunito', 'Quicksand', 'Pretendard', sans-serif;
      font-weight: 500;
      font-size: 16.5px;
      line-height: 1.55;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06);
    }

    .kakao-meta-col {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      flex-shrink: 0;
      line-height: 1.2;
    }

    .kakao-msg-row.me .kakao-meta-col {
      align-items: flex-end;
    }

    .kakao-unread {
      font-size: 11.5px;
      font-weight: 600;
      color: var(--kakao-unread);
      margin-bottom: 2px;
    }

    .kakao-time {
      font-size: 11px;
      color: #556475;
      white-space: nowrap;
    }

    .translate-btn {
      align-self: flex-start;
      margin-top: 7px;
      background: rgba(255, 255, 255, 0.85);
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-radius: 999px;
      padding: 4px 12px;
      font-size: 13px;
      color: #3D4A59;
      cursor: pointer;
      transition: background 0.2s;
    }

    .translate-btn:hover {
      background: #FFFFFF;
    }

    .translated-text {
      display: none;
      margin-top: 6px;
      padding: 10px 14px;
      background: rgba(255, 255, 255, 0.92);
      border-left: 3px solid #FEE500;
      border-radius: 10px;
      font-size: 15px;
      color: var(--text-primary);
      line-height: 1.55;
    }

    /* 카톡 하단 짝꿍 미션 패널 */
    .mission-box {
      background: #FFFFFF;
      border-top: 1px solid var(--border-light);
      border-radius: 24px 24px 0 0;
      padding: 20px 22px 24px;
      margin-top: auto;
      box-shadow: 0 -6px 20px rgba(0, 0, 0, 0.04);
    }

    .mission-title {
      font-size: 16.5px;
      color: var(--text-primary);
      margin-bottom: 12px;
      line-height: 1.5;
    }

    .option-list {
      display: flex;
      flex-direction: column;
      gap: 9px;
    }

    .option-btn {
