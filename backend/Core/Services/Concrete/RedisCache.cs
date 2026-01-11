using Core.Services.Abstract;
using StackExchange.Redis;
using System.Text.Json;

namespace Core.Services.Concrete
{
    public class RedisCacheService : IRedisCacheService
    {
        private readonly IDatabase _cache;
        public RedisCacheService(IConnectionMultiplexer redis)
        {
            _cache = redis.GetDatabase();
        }

        public async Task SetAsync<T>(string key, T value, TimeSpan? expiry = null)
        {
            var json = JsonSerializer.Serialize(value);
            await (expiry.HasValue ? 
            _cache.StringSetAsync(key, json, expiry.Value) 
            : _cache.StringSetAsync(key, json));
        }

        public async Task<T?> GetAsync<T>(string key){
            var value = await _cache.StringGetAsync(key);
            if (value.IsNullOrEmpty) return default;
            return JsonSerializer.Deserialize<T>(value!);
        }

        public async Task RemoveAsync(string key)
        {
            await _cache.KeyDeleteAsync(key);
        }
    }
}