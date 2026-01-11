

namespace Core.Services.Abstract
{
    public interface IRedisCacheService
    {
        public Task<T> GetAsync<T>(string key);
        public Task SetAsync<T>(string key, T value, TimeSpan? expiry = null);
        public Task RemoveAsync(string key);
    }
}