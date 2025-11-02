Here's a pattern I keep seeing:

.capabilities-section {
      background: white;
      padding: 60px 20px;
      overflow: hidden;
      position: relative;
    }
    
    .capabilities-section h2 {
      text-align: center;
      color: var(--rust-dark);
      font-size: 2.5rem;
      margin-bottom: 50px;
    }
    
    .carousel-container {
      position: relative;
      width: 100%;
      overflow: hidden;
      padding: 20px 60px;
    }
    
    .carousel-container::before,
    .carousel-container::after {
      content: '';
      position: absolute;
      top: 0;
      bottom: 0;
      width: 120px;
      z-index: 2;
      pointer-events: none;
    }
    
    .carousel-container::before {
      left: 0;
      background: linear-gradient(to right, white, transparent);
    }
    
    .carousel-container::after {
      right: 0;
      background: linear-gradient(to left, white, transparent);
    }
    
    .carousel-nav {
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      z-index: 3;
      background: var(--rust);
      color: white;
      border: none;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      transition: all 0.3s ease;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .carousel-nav:hover {
      background: var(--rust-dark);
      transform: translateY(-50%) scale(1.1);
    }
    
    .carousel-nav.prev { left: 10px; }
    .carousel-nav.next { right: 10px; }
    
    .carousel-track {
      display: flex;
      gap: 20px;
      animation: scroll 40s linear infinite;
    }
    
    .carousel-track:hover {
      animation-play-state: paused;
    }
    
    .carousel-track-wrapper {
      display: flex;
      gap: 20px;
    }
    
    @keyframes scroll {
      0% { transform: translateX(0); }
      100% { transform: translateX(-50%); }
    }
    
    .capability-card {
      flex: 0 0 280px;
      background: var(--cream);
      padding: 24px;
      border-radius: 12px;
      border: 2px solid var(--gold);
      display: flex;
      flex-direction: column;
      gap: 12px;
      min-height: 200px;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .capability-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 6px 20px rgba(139, 58, 31, 0.15);
    }
    
    .capability-number {
      width: 36px;
      height: 36px;
      background: var(--rust);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 16px;
      flex-shrink: 0;
    }
    
    .capability-card h3 {
      color: var(--rust-dark);
      font-size: 16px;
      line-height: 1.3;
      margin: 0;
    }
    
    .capability-card p {
      color: var(--gray);
      font-size: 13px;
      line-height: 1.5;
      margin: 0;
    }

—
What stands out to you? What would you add?