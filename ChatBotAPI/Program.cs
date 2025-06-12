using Microsoft.EntityFrameworkCore;
using ChatBotAPI.Data;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "ChatBot API", Version = "v1" });
});

// Configure HttpClient
builder.Services.AddHttpClient("PythonBackend", client =>
{
    client.BaseAddress = new Uri("http://localhost:9000/");
    client.DefaultRequestHeaders.Add("Accept", "application/json");
});

// Configure Database
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "ChatBot API V1");
        c.RoutePrefix = "swagger";
    });
}

// Configure HTTPS
app.UseHttpsRedirection();
app.UseRouting();
app.UseAuthorization();
app.MapControllers();

app.Run();
