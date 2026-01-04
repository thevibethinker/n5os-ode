/**
 * Native TypeScript Protection Checker
 *
 * Replaces Python subprocess (n5_protect.py) with native TypeScript
 * for O(1) protection checks with in-memory caching.
 *
 * Part of N5 System Optimization - Workstream 3.
 */

import * as fs from "fs";
import * as path from "path";

/**
 * Structure of .n5protected marker files
 */
interface N5ProtectedMarker {
  protected: boolean;
  reason?: string;
  created?: string;
  created_by?: string;
  patterns?: string[];
  metadata?: Record<string, unknown>;
}

/**
 * Result of a protection check
 */
export interface ProtectionCheckResult {
  protected: boolean;
  reason?: string;
  protectedBy?: string;
  cached?: boolean;
}

/**
 * Cached marker entry with timestamp
 */
interface CachedMarker {
  marker: N5ProtectedMarker | null;
  loadedAt: number;
}

/**
 * ProtectionChecker - Native TypeScript protection rule checker
 *
 * Provides fast protection checking with in-memory caching of .n5protected
 * marker files. Eliminates the 300ms Python subprocess overhead.
 *
 * Usage:
 * ```typescript
 * const checker = new ProtectionChecker();
 * const result = checker.isProtected('/home/workspace/N5/prefs/some_file.json');
 * if (result.protected) {
 *   console.log(`Protected: ${result.reason}`);
 * }
 * ```
 */
export class ProtectionChecker {
  private markerCache: Map<string, CachedMarker> = new Map();
  private readonly CACHE_TTL_MS: number;
  private lastCacheClear: number = Date.now();
  private readonly workspaceRoot: string;

  /**
   * Create a new ProtectionChecker
   *
   * @param options Configuration options
   * @param options.cacheTtlMs Cache TTL in milliseconds (default: 60000 = 1 minute)
   * @param options.workspaceRoot Root workspace path (default: /home/workspace)
   */
  constructor(options?: { cacheTtlMs?: number; workspaceRoot?: string }) {
    this.CACHE_TTL_MS = options?.cacheTtlMs ?? 60000;
    this.workspaceRoot = options?.workspaceRoot ?? "/home/workspace";
  }

  /**
   * Check if a path is protected by N5 rules.
   *
   * Walks up the directory tree from the target path, checking for
   * .n5protected marker files at each level.
   *
   * @param targetPath Path to check (absolute or relative)
   * @returns Protection check result
   */
  isProtected(targetPath: string): ProtectionCheckResult {
    this.maybeClearCache();

    const absolutePath = path.resolve(targetPath);
    let currentPath = absolutePath;

    // Walk up directory tree looking for .n5protected markers
    while (currentPath.length > 1) {
      // Check if current directory has a marker
      const checkDir = fs.statSync(currentPath, { throwIfNoEntry: false })?.isDirectory()
        ? currentPath
        : path.dirname(currentPath);

      const marker = this.getMarker(checkDir);

      if (marker?.protected) {
        // Check if path matches any exclusion patterns (if specified)
        if (!marker.patterns || marker.patterns.length === 0 || this.matchesPatterns(absolutePath, marker.patterns)) {
          return {
            protected: true,
            reason: marker.reason || `Protected by ${checkDir}/.n5protected`,
            protectedBy: checkDir,
            cached: this.markerCache.has(checkDir),
          };
        }
      }

      // Move up to parent directory
      const parentPath = path.dirname(currentPath);
      if (parentPath === currentPath) {
        break; // Reached root
      }
      currentPath = parentPath;

      // Stop at workspace root
      if (currentPath === this.workspaceRoot || currentPath.length < this.workspaceRoot.length) {
        break;
      }
    }

    return { protected: false };
  }

  /**
   * Get marker for a directory, using cache when available.
   *
   * @param dirPath Directory path to check
   * @returns Marker data or null if no marker exists
   */
  private getMarker(dirPath: string): N5ProtectedMarker | null {
    const cached = this.markerCache.get(dirPath);

    // Return cached value if still valid
    if (cached && Date.now() - cached.loadedAt < this.CACHE_TTL_MS) {
      return cached.marker;
    }

    // Load from disk
    const markerPath = path.join(dirPath, ".n5protected");
    let marker: N5ProtectedMarker | null = null;

    try {
      if (fs.existsSync(markerPath)) {
        const content = fs.readFileSync(markerPath, "utf-8");
        marker = JSON.parse(content);
      }
    } catch {
      // Invalid JSON or read error - treat as no marker
      marker = null;
    }

    // Cache the result (including null for directories without markers)
    this.markerCache.set(dirPath, {
      marker,
      loadedAt: Date.now(),
    });

    return marker;
  }

  /**
   * Check if path matches any of the protection patterns.
   *
   * @param targetPath Path to check
   * @param patterns Glob patterns to match against
   * @returns True if path matches any pattern (or if no patterns specified)
   */
  private matchesPatterns(targetPath: string, patterns: string[]): boolean {
    if (!patterns || patterns.length === 0) {
      return true; // No patterns = protect everything
    }

    // Simple glob matching - convert glob to regex
    return patterns.some((pattern) => {
      const regex = new RegExp(
        "^" +
          pattern
            .replace(/[.+^${}()|[\]\\]/g, "\\$&") // Escape regex special chars
            .replace(/\*/g, ".*") // * matches any characters
            .replace(/\?/g, ".") + // ? matches single character
          "$"
      );
      return regex.test(targetPath);
    });
  }

  /**
   * Clear cache if TTL has expired.
   */
  private maybeClearCache(): void {
    if (Date.now() - this.lastCacheClear > this.CACHE_TTL_MS) {
      this.markerCache.clear();
      this.lastCacheClear = Date.now();
    }
  }

  /**
   * Manually clear the cache.
   * Useful when protection rules have changed.
   */
  clearCache(): void {
    this.markerCache.clear();
    this.lastCacheClear = Date.now();
  }

  /**
   * Invalidate cache for a specific directory.
   *
   * @param dirPath Directory path to invalidate
   */
  invalidateCache(dirPath: string): void {
    this.markerCache.delete(dirPath);
  }

  /**
   * Get cache statistics for debugging.
   *
   * @returns Cache statistics
   */
  getCacheStats(): { size: number; ttlMs: number; lastClearAt: number } {
    return {
      size: this.markerCache.size,
      ttlMs: this.CACHE_TTL_MS,
      lastClearAt: this.lastCacheClear,
    };
  }

  /**
   * Format protection result for display (matches Python output format).
   *
   * @param result Protection check result
   * @param targetPath Original path that was checked
   * @returns Formatted string for display
   */
  formatResult(result: ProtectionCheckResult, targetPath: string): string {
    if (result.protected) {
      const lines = [
        `⚠️  PROTECTED: ${targetPath}`,
        `Reason: ${result.reason || "Protected directory"}`,
      ];
      if (result.protectedBy) {
        lines.push(`Protected by: ${result.protectedBy}`);
      }
      return lines.join("\n");
    }
    return `✓ Not protected: ${targetPath}`;
  }
}

// Export singleton for convenience
export const protectionChecker = new ProtectionChecker();
