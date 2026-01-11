using Core.Services.Abstract;
using Core.Services.Concrete;
using Infra.Repositories;  

namespace Application.Extensions
{
    public static class ApplicationServiceExtensions
    {
        public static IServiceCollection AddApplicationServices(this IServiceCollection services)
        {
             services.AddScoped<IUsersRepository, UsersRepository>();

            services.AddScoped<IUsersService, UserServices>();
            services.AddScoped<IRedisCacheService, RedisCacheService>();

            return services;
        }
    }
}