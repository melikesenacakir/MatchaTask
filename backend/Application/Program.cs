using Application.Extensions;
using Infra.Database;
using Microsoft.EntityFrameworkCore;
using StackExchange.Redis;

var builder = WebApplication.CreateBuilder(args);


builder.Services.AddApiServices();
builder.Services.AddDatabaseServices(builder.Configuration);  
builder.Services.AddApplicationServices();
builder.Services.AddAutoMapper(typeof(Program).Assembly);

builder.Services.AddCorsPolicy();


builder.Services.AddSingleton<IConnectionMultiplexer>(sp =>
{
    var configuration = builder.Configuration.GetConnectionString("Redis");
    return ConnectionMultiplexer.Connect(configuration);
});



var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ApplicationDB>();
    try
    {
        await db.Database.MigrateAsync();
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Database migration error: {ex.Message}");
    }
}


if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors()
   .UseAuthentication()
   .UseAuthorization();
   
app.MapControllers();

app.Run();