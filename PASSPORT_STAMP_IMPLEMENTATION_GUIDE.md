# Steam Gaming Credentials Passport Stamp - Implementation Guide

## Executive Summary

This guide outlines the implementation steps needed to integrate Steam Gaming Credentials as a Passport Stamp. The stamp verifies a user's Steam gaming activity against specific criteria to establish credibility and genuine engagement.

**Based on:** OAuth stamp patterns from Gitcoin Passport repository (Google, Discord, LinkedIn implementations)

---

## 1. Stamp Overview

### Qualification Criteria

Users must meet ALL of the following requirements:
- ✅ **100+ hours total playtime** across all games
- ✅ **10+ achievements earned** across all games
- ✅ **3+ games with >1 hour** each of playtime
- ✅ **≤50% playtime** in any single game (demonstrates diversity)

### Stamp Purpose

This stamp serves to:
- Verify genuine long-term gaming engagement (not bot/sybil accounts)
- Demonstrate platform diversity (not single-game focused)
- Establish Steam account ownership
- Provide a high-signal credential for gaming-related initiatives

---

## 2. User-Facing Content

### Platform Details (Providers-config.ts)

Based on the pattern from existing OAuth stamps:

```typescript
export const PlatformDetails: PlatformSpec = {
  icon: "./assets/steamStampIcon.svg",
  platform: "Steam",
  name: "Steam",
  description: "Verify your Steam gaming credentials and activity",
  connectMessage: "Check Eligibility",
  website: "https://steamcommunity.com/",
  timeToGet: "2-3 minutes",
  price: "Free",
  guide: [
    {
      type: "steps",
      items: [
        {
          title: "Step 1",
          description: "Ensure your Steam Profile and Game Details are both set to Public in Privacy Settings.",
          actions: [
            {
              label: "Steam Privacy Settings",
              href: "https://steamcommunity.com/my/edit/settings",
            },
          ],
        },
        {
          title: "Step 2",
          description: "Click 'Check Eligibility' to connect and verify your Steam account.",
        },
        {
          title: "Step 3",
          description: "Your gaming activity will be automatically verified against qualification criteria.",
        },
      ],
    },
    {
      type: "list",
      title: "Important considerations",
      items: [
        "Both your Steam Profile and Game Details must be set to Public for verification to work",
        "Verification checks your total playtime, achievements, and game diversity",
        "You must meet ALL four criteria to receive this stamp",
        "Private profiles or profiles without sufficient gaming history will not qualify",
        "Your privacy settings can be changed back to private after verification is complete",
      ],
    },
  ],
};

export const ProviderConfig: PlatformGroupSpec[] = [
  {
    platformGroup: "Gaming Credentials",
    providers: [
      {
        title: "Verify Steam Gaming Credentials",
        description: "Connect your Steam account and verify gaming activity meets qualification criteria: 100+ hours playtime, 10+ achievements, 3+ games with >1 hour each, and no more than 50% playtime in a single game.",
        name: "SteamGamingCredentials",
      },
    ],
  },
];
```

### Provider Names

- **Platform ID:** `Steam`
- **Provider ID:** `SteamGamingCredentials`
- **Display Name:** "Steam Gaming Credentials"

---

## 3. Technical Implementation

### 3.1 File Structure

Create the following files in the Passport repository:

```
/passport/platforms/src/Steam/
├── index.ts                              # Module exports
├── App-Bindings.ts                       # Frontend Steam OpenID flow
├── Providers-config.ts                   # UI metadata and descriptions
├── Providers/
│   ├── index.ts                          # Provider exports
│   └── steamGamingCredentials.ts         # Verification logic
└── __tests__/
    └── steamGamingCredentials.test.ts    # Jest tests
```

### 3.2 Steam Authentication Approach

**Important:** Steam uses **OpenID 2.0**, NOT OAuth 2.0

Unlike Google/Discord/LinkedIn, Steam's authentication differs:
- Uses OpenID 2.0 protocol
- Returns a `claimed_id` (not access token)
- Format: `https://steamcommunity.com/openid/id/{STEAM_ID_64}`
- No client_secret required for OpenID validation

### 3.3 Frontend Implementation (App-Bindings.ts)

```typescript
export class SteamPlatform extends Platform {
  platformId = "Steam";
  path = "Steam";
  redirectUri: string = null;
  realm: string = null;

  constructor(options: PlatformOptions = {}) {
    super();
    this.redirectUri = options.redirectUri as string;
    this.realm = options.realm as string;
  }

  async getOAuthUrl(state: string): Promise<string> {
    const params = new URLSearchParams({
      "openid.ns": "http://specs.openid.net/auth/2.0",
      "openid.mode": "checkid_setup",
      "openid.return_to": `${this.redirectUri}?state=${state}`,
      "openid.realm": this.realm,
      "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
      "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    });

    return `https://steamcommunity.com/openid/login?${params.toString()}`;
  }
}
```

### 3.4 Backend Verification Logic (Providers/steamGamingCredentials.ts)

**Key Components:**

1. **Extract Steam ID** from OpenID response
2. **Fetch user's games** via Steam Web API
3. **Fetch achievement data** for each game
4. **Calculate qualification metrics**
5. **Return verification result**

**Pseudocode Structure:**

```typescript
export class SteamGamingCredentialsProvider implements Provider {
  type = "SteamGamingCredentials";

  async verify(payload: RequestPayload): Promise<VerifiedPayload> {
    try {
      // 1. Extract Steam ID from OpenID claimed_id
      const steamId = extractSteamId(payload.proofs.claimedId);

      if (!steamId) {
        return {
          valid: false,
          errors: ["Invalid Steam OpenID response"],
        };
      }

      // 2. Fetch gaming data from Steam API
      const gamingData = await fetchSteamGamingData(steamId);

      // 3. Calculate qualification criteria
      const qualifications = calculateQualifications(gamingData);

      // 4. Check if all criteria are met
      const valid =
        qualifications.totalPlaytimeHours >= 100 &&
        qualifications.totalAchievements >= 10 &&
        qualifications.gamesOver1Hr >= 3 &&
        qualifications.mostPlayedPercentage <= 50;

      if (valid) {
        return {
          valid: true,
          record: {
            steamId: steamId,
            totalPlaytime: qualifications.totalPlaytimeHours,
            achievements: qualifications.totalAchievements,
            gamesOver1Hr: qualifications.gamesOver1Hr,
            mostPlayedPercentage: qualifications.mostPlayedPercentage,
          },
          errors: [],
        };
      } else {
        return {
          valid: false,
          errors: [
            "Steam account does not meet qualification criteria. " +
            "Required: 100+ hours, 10+ achievements, 3+ games >1hr, ≤50% in single game."
          ],
        };
      }
    } catch (error) {
      throw new ProviderExternalVerificationError(
        `Steam verification error: ${String(error)}`
      );
    }
  }
}

// Helper: Extract Steam ID from OpenID claimed_id
function extractSteamId(claimedId: string): string | null {
  const match = claimedId.match(/^https:\/\/steamcommunity\.com\/openid\/id\/(\d{17})$/);
  return match ? match[1] : null;
}

// Helper: Fetch gaming data from Steam Web API
async function fetchSteamGamingData(steamId: string) {
  const apiKey = process.env.STEAM_API_KEY;

  // Fetch owned games
  const gamesResponse = await axios.get(
    `http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/`,
    {
      params: {
        key: apiKey,
        steamid: steamId,
        format: 'json',
        include_appinfo: true,
        include_played_free_games: true,
      }
    }
  );

  const games = gamesResponse.data.response.games || [];

  // Fetch achievements for each played game
  const achievementPromises = games
    .filter(game => game.playtime_forever > 0)
    .map(game => fetchGameAchievements(steamId, game.appid, apiKey));

  const achievementsData = await Promise.all(achievementPromises);

  return {
    games,
    achievements: achievementsData.flat(),
  };
}

// Helper: Fetch achievements for a specific game
async function fetchGameAchievements(steamId: string, appId: number, apiKey: string) {
  try {
    const response = await axios.get(
      `http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/`,
      {
        params: {
          appid: appId,
          key: apiKey,
          steamid: steamId,
        }
      }
    );

    const achievements = response.data.playerstats?.achievements || [];
    return achievements.filter(ach => ach.achieved === 1);
  } catch (error) {
    // Game might not have achievements or stats not available
    return [];
  }
}

// Helper: Calculate qualification metrics
function calculateQualifications(gamingData: any) {
  const { games } = gamingData;

  // Total playtime in hours
  const totalPlaytimeMinutes = games.reduce(
    (sum, game) => sum + (game.playtime_forever || 0),
    0
  );
  const totalPlaytimeHours = totalPlaytimeMinutes / 60;

  // Games with >1 hour
  const gamesOver1Hr = games.filter(game => game.playtime_forever > 60).length;

  // Most played game percentage
  const mostPlayedMinutes = Math.max(...games.map(g => g.playtime_forever || 0));
  const mostPlayedPercentage = totalPlaytimeMinutes > 0
    ? (mostPlayedMinutes / totalPlaytimeMinutes) * 100
    : 0;

  // Total achievements
  const totalAchievements = gamingData.achievements.length;

  return {
    totalPlaytimeHours,
    gamesOver1Hr,
    mostPlayedPercentage,
    totalAchievements,
  };
}
```

### 3.5 Environment Variables Required

Add to IAM service `.env`:

```bash
STEAM_API_KEY=your_steam_web_api_key_here
STEAM_CALLBACK=https://passport.xyz/auth/steam/callback
STEAM_REALM=https://passport.xyz
```

**Getting Steam API Key:**
- Register at: https://steamcommunity.com/dev/apikey
- Domain name: passport.xyz (or your domain)
- API key is free and instant

### 3.6 Register Platform

Add to `/passport/platforms/src/platforms.ts`:

```typescript
import { PlatformDetails as SteamPlatform, ProviderConfig as SteamProviderConfig, providers as SteamProviders } from "./Steam";

const platforms: Record<string, PlatformConfig> = {
  // ... existing platforms
  Steam: {
    ...SteamPlatform,
    providers: SteamProviderConfig,
    ProviderList: SteamProviders,
  },
  // ... other platforms
};
```

---

## 4. Verification Time Estimate

### Time Breakdown

**Estimated total time: 2-3 minutes**

1. **User Setup (30-60 seconds)**
   - Navigate to Steam Privacy Settings (if needed)
   - Set Game Details to Public
   - Return to Passport

2. **Authentication (15-30 seconds)**
   - Click "Connect Account"
   - Steam OpenID popup loads
   - User logs in to Steam (if not already)
   - Authorize and redirect back

3. **Verification Processing (60-90 seconds)**
   - Extract Steam ID from OpenID response: ~100ms
   - Fetch owned games from Steam API: ~500ms
   - Fetch achievements for played games (sequential): ~1-2 seconds
     - Depends on number of games played
     - Average 5-10 games = 5-10 API calls
   - Calculate metrics: ~10ms
   - Store credential: ~200ms

**Performance Optimization Considerations:**
- Achievement fetching is the bottleneck (multiple API calls)
- Could parallelize achievement requests (5-10 concurrent)
- Could implement caching for repeat verifications
- Could add timeout limits (30 seconds max)

**Comparison to Other Stamps:**
- Google: "< 1 minute" (single API call)
- Discord: "1-2 minutes" (single API call)
- Coinbase: "5 minutes" (requires external onchain verification)

**Recommended:** `"2-3 minutes"`

---

## 5. Important Considerations

### 5.1 Privacy & User Requirements

**Critical Requirements:**
- Steam **Profile** and **Game Details** must both be set to Public
- This is NOT the default setting for many users
- Private profiles will fail verification
- Clear instructions needed in UI

**User Communication:**
- Provide direct link to Steam Privacy Settings
- Explain WHY this is needed (to verify your gaming activity)
- Reassure users about data usage
- Note that settings can be changed back to private after verification
- Offer link to Steam's privacy documentation

### 5.2 Edge Cases to Handle

**Scenario 1: Private Profile**
- Error: "Unable to fetch gaming data"
- Solution: Direct user to change privacy settings
- UX: Show helpful error with settings link

**Scenario 2: New Steam Account**
- User may have account but insufficient gaming history
- Clear messaging: "Account does not meet minimum criteria"
- Don't show partial progress (prevents gaming the system)

**Scenario 3: API Rate Limiting**
- Steam API has rate limits
- Consider implementing exponential backoff
- Timeout after 30 seconds with helpful error

**Scenario 4: Games Without Achievements**
- Not all games have achievement systems
- Achievement check should gracefully handle 403/404 errors
- Still count playtime for such games

**Scenario 5: Free-to-Play Games**
- Include in playtime calculations
- May have achievements
- Use `include_played_free_games: true` parameter

### 5.3 Data Privacy & Storage

**What Gets Stored:**
```typescript
record: {
  steamId: string,           // User's Steam ID
  totalPlaytime: number,     // Total hours (rounded)
  achievements: number,      // Total achievement count
  gamesOver1Hr: number,      // Number of games >1hr
  mostPlayedPercentage: number, // Percentage of most-played game
}
```

**What Does NOT Get Stored:**
- Individual game names/titles
- Specific achievement details
- Friends list or social data
- Purchase history
- Any other Steam profile data

**Privacy Considerations:**
- Store only verification metrics, not raw data
- Don't expose which specific games user plays
- User can revoke Steam connection after verification
- Credential remains valid even if Steam profile becomes private later

### 5.4 Security Considerations

**OpenID Validation:**
- MUST validate the OpenID response properly
- Verify the signature from Steam
- Check return_to URL matches expected callback
- Validate nonce/state parameter to prevent CSRF

**API Key Security:**
- Store Steam API key in environment variables
- Never expose in frontend code
- Use server-side verification only
- Rotate key if compromised

**Rate Limiting:**
- Implement rate limiting on verification endpoint
- Prevent abuse/spamming of Steam API
- Consider per-user cooldown (e.g., once per hour)

### 5.5 Maintenance Considerations

**Steam API Dependencies:**
- Steam Web API is generally stable but:
  - Could change endpoints/parameters
  - Could implement stricter rate limits
  - Could deprecate certain data access
- Monitor for API changes and errors

**Criteria Updates:**
- Current criteria hardcoded in verification logic
- Consider making thresholds configurable
- Data scientist may want to adjust based on scoring data

**Testing:**
- Need test Steam accounts with various profiles:
  - One that qualifies
  - One with insufficient playtime
  - One with too many achievements in single game
  - One with private profile
- Mock Steam API responses in unit tests

---

## 6. Implementation Checklist

### Phase 1: Core Implementation
- [ ] Create `/platforms/src/Steam/` directory structure
- [ ] Implement `App-Bindings.ts` with Steam OpenID URL generation
- [ ] Implement `Providers-config.ts` with user-facing content
- [ ] Implement `steamGamingCredentials.ts` provider with verification logic
- [ ] Add Steam platform to `platforms.ts`
- [ ] Create Steam icon SVG asset

### Phase 2: Backend Setup
- [ ] Obtain Steam API Key from Steam Dev portal
- [ ] Add environment variables to IAM service
- [ ] Set up Steam callback URL routing
- [ ] Implement OpenID response validation
- [ ] Test Steam API integration

### Phase 3: Testing
- [ ] Write unit tests for provider verification logic
- [ ] Test with qualifying Steam account
- [ ] Test with non-qualifying accounts (various failure scenarios)
- [ ] Test with private Steam profile
- [ ] Test API error handling
- [ ] Performance testing (measure actual verification time)

### Phase 4: UI/UX
- [ ] Create Steam stamp icon
- [ ] Review user-facing text with product team
- [ ] Test privacy settings instructions with real users
- [ ] Ensure error messages are helpful and actionable

### Phase 5: Deployment
- [ ] Deploy to staging environment
- [ ] QA testing with multiple Steam accounts
- [ ] Monitor API usage and response times
- [ ] Deploy to production
- [ ] Monitor error rates and user feedback

### Phase 6: Post-Launch
- [ ] Collect data on verification success/failure rates
- [ ] Share metrics with data scientist for weight calculation
- [ ] Monitor Steam API stability
- [ ] Iterate on criteria based on data

---

## 7. Differences from Standard OAuth Stamps

### Steam vs. Google/Discord/LinkedIn

| Aspect | OAuth 2.0 (Google, etc.) | Steam OpenID 2.0 |
|--------|-------------------------|------------------|
| Protocol | OAuth 2.0 | OpenID 2.0 |
| Client Secret | Required | Not required |
| Access Token | Yes | No |
| User Identifier | From API response | From `claimed_id` |
| Additional API Calls | Optional | Required (Steam Web API) |
| Verification Complexity | Low | Medium-High |
| External Dependencies | 1 API | 2+ APIs (OpenID + Web API) |

### Additional Complexity Factors

1. **Multiple API Endpoints:**
   - OpenID for authentication
   - GetOwnedGames for game library
   - GetUserStatsForGame for achievements (per game)

2. **Qualification Logic:**
   - Other stamps: binary verification (have account or not)
   - Steam: complex multi-criteria validation

3. **Performance:**
   - Other stamps: 1-2 API calls
   - Steam: 1 + N API calls (where N = number of games played)

4. **Privacy Requirements:**
   - Explicit user action needed (make profile public)
   - Clear documentation required

---

## 8. Recommended Next Steps

### Immediate Actions

1. **Create Proof of Concept**
   - Use existing steam-sdk-test code as foundation
   - Adapt for Passport platform structure
   - Test with real Steam accounts

2. **Stakeholder Review**
   - Product team: Review user-facing text and UX
   - Security team: Review OpenID validation approach
   - Data scientist: Confirm criteria are appropriate for scoring

3. **Technical Validation**
   - Verify Steam API access and rate limits
   - Test OpenID flow in Passport environment
   - Benchmark verification performance

### Before Full Implementation

1. **Criteria Validation**
   - Confirm current criteria (100hr, 10 ach, 3 games, 50% diversity)
   - May need adjustment based on:
     - Average Steam user metrics
     - Desired selectivity
     - Gaming vs. bot account patterns

2. **Weight Determination**
   - Data scientist analyzes qualification data
   - Compares to other stamps (Discord, Google, etc.)
   - Assigns appropriate weight/score

3. **User Research**
   - Test privacy settings instructions with users
   - Validate time estimate is accurate
   - Gather feedback on error messages

---

## 9. Success Metrics

### Verification Success Rate
- **Target:** 70-80% of attempts succeed
- **Blockers to track:**
  - Private profiles (expected to be common)
  - Insufficient gaming history
  - API errors/timeouts

### Performance Metrics
- **Target verification time:** < 3 minutes for 95th percentile
- **API error rate:** < 5%
- **Timeout rate:** < 2%

### User Experience
- **Abandonment rate:** < 20% during verification flow
- **Support tickets:** Track common issues
- **Re-verification rate:** How often users retry

### Quality Signals
- **Qualification rate:** % of verified users who meet criteria
- **Anti-sybil effectiveness:** Compare with known sybil patterns
- **Score distribution:** Analyze after data scientist assigns weight

---

## 10. Alternative Approaches Considered

### Option A: Simplified Criteria (Not Recommended)
- Only check account age + total playtime
- Pros: Faster verification, simpler logic
- Cons: Easier to game, less signal

### Option B: Manual Review (Not Scalable)
- Human review of Steam profiles
- Pros: Most accurate
- Cons: Not scalable, slow, expensive

### Option C: Steam API Only (No OpenID)
- Users manually input Steam ID
- Pros: Simpler technical implementation
- Cons: No proof of ownership, easily spoofed

**Recommended: Current approach** (OpenID + criteria verification)
- Best balance of security, UX, and signal quality

---

## 11. Resources & References

### Steam Developer Documentation
- **Steam Web API:** https://partner.steamgames.com/doc/webapi
- **Steam OpenID:** https://steamcommunity.com/dev
- **API Key Registration:** https://steamcommunity.com/dev/apikey
- **Privacy Settings:** https://steamcommunity.com/my/edit/settings

### Passport Codebase References
- **Google Provider:** `/passport/platforms/src/Google/`
- **Discord Provider:** `/passport/platforms/src/Discord/`
- **LinkedIn Provider:** `/passport/platforms/src/Linkedin/`
- **Type Definitions:** `/passport/platforms/src/types.ts`
- **Platform Registry:** `/passport/platforms/src/platforms.ts`

### NPM Packages to Consider
- `passport-steam` - Steam OpenID authentication strategy
- `axios` - HTTP client (already used in Passport)
- Standard Passport libraries (already in use)

### Testing Resources
- Steam test accounts (create multiple)
- Steam API testing tools
- Passport local development environment

---

## 12. Risk Assessment

### High Risk
- **Steam API Changes:** Medium likelihood, High impact
  - Mitigation: Monitor Steam dev updates, version API calls
- **Privacy Requirements:** High likelihood of user confusion, Medium impact
  - Mitigation: Clear instructions, helpful error messages

### Medium Risk
- **Performance Issues:** Medium likelihood, Medium impact
  - Mitigation: Parallel API calls, caching, timeouts
- **Rate Limiting:** Low likelihood, High impact
  - Mitigation: Implement backoff, user cooldowns

### Low Risk
- **OpenID Protocol Changes:** Very low likelihood, High impact
  - Mitigation: OpenID 2.0 is stable, unlikely to change
- **Criteria Gaming:** Low likelihood, Low impact
  - Mitigation: Diverse criteria make gaming difficult

---

## Conclusion

The Steam Gaming Credentials stamp is feasible and provides high-signal verification data. The implementation follows established patterns in the Passport repository while accounting for Steam's unique OpenID authentication and complex qualification criteria.

**Key Differentiators:**
- Multi-criteria validation (not just account ownership)
- Gaming activity patterns (anti-sybil signal)
- Demonstrates long-term platform engagement

**Main Challenges:**
- More complex than typical OAuth stamps
- User privacy setting requirements
- Multiple API calls affecting performance
- Steam-specific OpenID 2.0 protocol

**Recommended Timeline:**
- POC: 1 week
- Full implementation: 2-3 weeks
- Testing & refinement: 1-2 weeks
- **Total: 4-6 weeks to production**

The proof-of-concept built in `steam-sdk-test/` demonstrates the core verification logic works. Next step is adapting this to the Passport platform structure and integrating with the existing IAM and credential issuance systems.
